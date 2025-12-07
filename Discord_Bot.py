import discord
import asyncio
import re
from datetime import datetime, timedelta
import random
from Telegram_Bot import TelegramBot  # Importiere den Telegram-Bot
import config

# Patch für discord.py-self Bug mit pending_payments
import discord.state
original_parse_ready_supplemental = discord.state.ConnectionState.parse_ready_supplemental

def patched_parse_ready_supplemental(self, data):
    # Fix: Ersetze None mit leerer Liste für pending_payments
    if 'pending_payments' in data and data['pending_payments'] is None:
        data['pending_payments'] = []
    elif 'pending_payments' not in data:
        data['pending_payments'] = []
    return original_parse_ready_supplemental(self, data)

discord.state.ConnectionState.parse_ready_supplemental = patched_parse_ready_supplemental

# Pfade zu externen Dateien
BALLS_FILE = "balls.py"
CONFIG_FILE = "config.py"

class SelfBot(discord.Client):
    def __init__(self, telegram_bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.telegram_bot = telegram_bot  # Telegram-Bot Instanz
        self.balls = self.load_balls()
        self.last_sent_date, self.bot_enabled, self.token, self.channel_id, self.message, self.target_username, self.timeframe = self.load_config()

    def load_balls(self):
        try:
            from balls import LIST
            return {ball["Name"].lower(): ball for ball in LIST}
        except ImportError:
            self.log_to_telegram(f"The file {BALLS_FILE} could not be imported.")
            return {}

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = file.read()

                date_match = re.search(r"DiscordDate = \"(\d{2}-\d{2}-\d{4})\"", config)
                bot_match = re.search(r"BotDiscord = (true|false)", config, re.IGNORECASE)
                token_match = re.search(r"DiscordToken = \"(.*?)\"", config)
                channel_match = re.search(r"DiscordChannel = (\d+)", config)
                message_match = re.search(r"DiscordMessage = \"(.*?)\"", config)
                username_match = re.search(r"DiscordUsername = \"(.*?)\"", config)
                time_match = re.search(r"DiscordMessageTime = \"(\d{2}:\d{2})\"", config)
                delay_match = re.search(r"DiscordMessageDelay = \"(\d+)\"", config)

                # Parse the date in DD-MM-YYYY format
                last_date = datetime.strptime(date_match.group(1), "%d-%m-%Y").strftime("%Y-%m-%d") if date_match else None
                bot_enabled = bot_match.group(1).lower() == "true" if bot_match else False
                token = token_match.group(1) if token_match else None
                channel_id = int(channel_match.group(1)) if channel_match else None
                message = message_match.group(1) if message_match else "!pokeda"
                target_username = username_match.group(1) if username_match else ""

                # Parse DiscordMessageTime and DiscordMessageDelay
                if time_match and delay_match:
                    start_time = datetime.strptime(time_match.group(1), "%H:%M").time()
                    delay_minutes = int(delay_match.group(1))
                    end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=delay_minutes)).time()
                    timeframe = (start_time, delay_minutes)
                else:
                    timeframe = None

                if not bot_enabled:
                    self.log_to_telegram("BotDiscord is disabled.")
                if not token:
                    self.log_to_telegram("Error: DiscordToken is missing in the configuration file.")
                if not channel_id:
                    self.log_to_telegram("Error: DiscordChannel is missing in the configuration file.")
                if not target_username:
                    self.log_to_telegram("Error: DiscordUsername is missing in the configuration file.")

                return last_date, bot_enabled, token, channel_id, message, target_username, timeframe
        except FileNotFoundError:
            self.log_to_telegram(f"The file {CONFIG_FILE} was not found.")
            return None, False, None, None, "!pokeda", "", None
        
    #Sends a log message to the Telegram bot and prints it to the console.
    def log_to_telegram(self, text):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.telegram_bot.send_message(text))
        except RuntimeError:
            # Wenn kein Loop läuft, ignoriere die Nachricht oder logge sie nur lokal
            print(text)

    async def on_ready(self):
        if not self.bot_enabled or not self.token or not self.channel_id:
            self.log_to_telegram("The DiscordBot is disabled or insufficiently configured. Exiting...")
            await self.close()
            return

        # Calculate next scheduled message time
        if self.timeframe:
            base_time, delay_minutes = self.timeframe
            today = datetime.now().date()
            base_datetime = datetime.combine(today, base_time)
            random_delay = random.randint(0, delay_minutes * 60)
            scheduled_time = base_datetime + timedelta(seconds=random_delay)
            now = datetime.now()
            if scheduled_time < now:
                scheduled_time += timedelta(days=1)
            next_time_str = scheduled_time.strftime("%H:%M")
            next_date_str = scheduled_time.strftime("%d.%m.%Y")
            startup_msg = (
                f"DiscordBot started!\n"
                f"Logged in on Discord as User {config.DiscordUsername}\n"
                f"The next daily reward will be sent at:\n{next_time_str} on {next_date_str}."
            )
            print(startup_msg)
            self.log_to_telegram(startup_msg)
            delay_seconds = (scheduled_time - datetime.now()).total_seconds()
            await asyncio.sleep(delay_seconds)
            await self.send_daily_message()
        else:
            startup_msg = (
                f"DiscordBot started!\n"
                f"Logged in on Discord as User {config.DiscordUsername}\n"
                f"No valid timeframe for Discord Message specified."
            )
            print(startup_msg)
            self.log_to_telegram(startup_msg)

    async def schedule_daily_message(self):
        if not self.timeframe:
            self.log_to_telegram("No valid timeframe for Discord Message specified. The message will not be scheduled.")
            return

        today = datetime.now().date()

        if self.last_sent_date == today.strftime("%Y-%m-%d"):
            base_time, delay_minutes = self.timeframe
            base_datetime = datetime.combine(datetime.now().date() + timedelta(days=1), base_time)
            random_delay = random.randint(0, delay_minutes * 60)
            scheduled_time = base_datetime + timedelta(seconds=random_delay)
            next_time_str = scheduled_time.strftime("%H:%M")
            next_date_str = scheduled_time.strftime("%d.%m.%Y")
            msg = (
                "You already claimed your reward today!\n"
                f"The next daily reward can be claimed at:\n{next_time_str} on {next_date_str}."
            )
            print(msg)
            self.log_to_telegram(msg)
            delay_seconds = (scheduled_time - datetime.now()).total_seconds()
            await asyncio.sleep(delay_seconds)
            await self.send_daily_message()
            return

        base_time, delay_minutes = self.timeframe
        base_datetime = datetime.combine(today, base_time)
        random_delay = random.randint(0, delay_minutes * 60)
        scheduled_time = base_datetime + timedelta(seconds=random_delay)
        now = datetime.now()
        if scheduled_time < now:
            scheduled_time += timedelta(days=1)
        delay_seconds = (scheduled_time - now).total_seconds()
        await asyncio.sleep(delay_seconds)
        await self.send_daily_message()

    async def send_daily_message(self):
        channel = self.get_channel(self.channel_id)
        if channel is None:
            self.log_to_telegram("Discord Channel not found! Please check the DiscordChannel in the config.py file.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_sent_date == today:
            self.log_to_telegram("The Discord message has already been sent today.")
            if self.timeframe:
                base_time, delay_minutes = self.timeframe
                base_datetime = datetime.combine(datetime.now().date() + timedelta(days=1), base_time)
                random_delay = random.randint(0, delay_minutes * 60)
                scheduled_time = base_datetime + timedelta(seconds=random_delay)
                next_time_str = scheduled_time.strftime("%H:%M")
                next_date_str = scheduled_time.strftime("%d.%m.%Y")
                self.log_to_telegram(
                    f"The next daily reward can be claimed at:\n{next_time_str} on {next_date_str}."
                )
                delay_seconds = (scheduled_time - datetime.now()).total_seconds()
                await asyncio.sleep(delay_seconds)
                await self.send_daily_message()
            return

        try:
            await channel.send(self.message)
            self.log_to_telegram(f"Discord Message sent: {self.message}")
            self.last_sent_date = today
            self.save_config(today)
            if self.timeframe:
                base_time, delay_minutes = self.timeframe
                base_datetime = datetime.combine(datetime.now().date() + timedelta(days=1), base_time)
                random_delay = random.randint(0, delay_minutes * 60)
                scheduled_time = base_datetime + timedelta(seconds=random_delay)
                next_time_str = scheduled_time.strftime("%H:%M")
                next_date_str = scheduled_time.strftime("%d.%m.%Y")
                self.log_to_telegram(
                    f"The next daily reward will be sent at:\n{next_time_str} on {next_date_str}."
                )
                delay_seconds = (scheduled_time - datetime.now()).total_seconds()
                await asyncio.sleep(delay_seconds)
                await self.send_daily_message()
        except Exception as e:
            self.log_to_telegram(f"Error while sending the Discord message: {e}")

    async def on_message(self, message):
        if message.channel.id != self.channel_id or message.author == self.user:
            return

        # Check if your user ID is mentioned in the message
        if not any(user.id == config.DiscordUserID for user in message.mentions):
            return  # Ignore messages not mentioning your user ID

        print("Mentions in message:", message.mentions)
        print("My user:", self.user)
        print("Config user ID:", config.DiscordUserID)

        # Now handle the message as before
        if "You already have claimed your daily reward" in message.content:
            reward_start = message.content.find("Your last reward:")
            if reward_start != -1:
                reward_text = message.content[reward_start:].strip()
            else:
                reward_text = message.content.strip()

            # Remove Discord emoji codes
            cleaned_reward = re.sub(r"<:[^:]+:\d+>", "", reward_text)

            # Extract only the lines with items or money (e.g. "$7", "1x Poke Ball")
            item_lines = []
            for line in cleaned_reward.splitlines():
                line = line.strip()
                if re.match(r"^\$?\d+(\s*x\s*[\w\s]+)?$", line) or "x " in line:
                    item_lines.append(line)

            # Prepare next claim time
            next_message_time = self.parse_next_message_time(message.content)
            if next_message_time:
                next_time_str = next_message_time.strftime("%H:%M")
                next_date_str = next_message_time.strftime("%d.%m.%Y")
                summary = (
                    "You already claimed your items today. The reward was:\n"
                    + "\n".join(item_lines)
                    + f"\n\nThe next daily reward can be claimed at:\n{next_time_str} on {next_date_str}."
                )
                self.log_to_telegram(summary)
                if self.is_auto_time_enabled():
                    self.update_discord_message_time(next_time_str)
                new_date = next_message_time.strftime("%Y-%m-%d")
                self.save_config(new_date)
                # Always pause until next time
                delay_seconds = (next_message_time - datetime.now()).total_seconds()
                print(f"Sleeping for {delay_seconds} seconds until next daily message.")
                await asyncio.sleep(delay_seconds)
                await self.send_daily_message()
            return

        # Handle other messages directed to you
        cleaned_message, items_received = self.parse_message(message.content)
        if items_received:
            self.update_inventory(items_received)
            # Build the reward summary
            reward_lines = [f"Your daily reward today was:"]
            for item, amount in items_received.items():
                reward_lines.append(f" {amount}x {item}" if not item.startswith("$") else f" {item}")
            reward_summary = "\n".join(reward_lines)

            # Calculate next message time
            base_time, delay_minutes = self.timeframe
            base_datetime = datetime.combine(datetime.now().date() + timedelta(days=1), base_time)
            random_delay = random.randint(0, delay_minutes * 60)
            next_message_time = base_datetime + timedelta(seconds=random_delay)
            next_time_str = next_message_time.strftime("%H:%M")
            next_date_str = next_message_time.strftime("%d.%m.%Y")

            # Send summary with next claim info
            summary = (
                reward_summary +
                f"\n\nThe next daily reward can be claimed at:\n{next_time_str} on {next_date_str}."
            )
            self.log_to_telegram(summary)
            if self.is_auto_time_enabled():
                self.update_discord_message_time(next_time_str)
            new_date = next_message_time.strftime("%Y-%m-%d")
            self.save_config(new_date)
            delay_seconds = (next_message_time - datetime.now()).total_seconds()
            print(f"Sleeping for {delay_seconds} seconds until next daily message.")
            await asyncio.sleep(delay_seconds)
            await self.send_daily_message()
        return

    def parse_message(self, content):
        # Remove Discord-specific emojis like <:rarity_common:800452290351726602>
        cleaned_message = re.sub(r"<:[^:]+:\d+>", "", content).strip()

        # Extract items received (e.g., "1x Poke Ball")
        item_matches = re.findall(r"(\d+)x ([\w\s]+)", cleaned_message)
        items_received = {item_name.strip(): int(quantity) for quantity, item_name in item_matches}

        return cleaned_message, items_received

    def parse_next_message_time(self, content):
        try:
            # Extract the time remaining (e.g., "19 hours, 40 minutes, and 52 seconds")
            time_match = re.search(r"(\d+)\s*hours?,\s*(\d+)\s*minutes?(?:,\s*(\d+)\s*seconds?)?", content)
            if not time_match:
                return None

            hours = int(time_match.group(1))
            minutes = int(time_match.group(2))
            seconds = int(time_match.group(3)) if time_match.group(3) else 0

            # Calculate the base next message time
            next_message_time = datetime.now() + timedelta(hours=hours, minutes=minutes, seconds=seconds)

            # Add a random delay based on DiscordMessageDelay
            random_delay_minutes = random.randint(0, int(self.timeframe[1]))
            next_message_time += timedelta(minutes=random_delay_minutes)

            return next_message_time
        except Exception as e:
            self.log_to_telegram(f"Error while parsing next message time: {e}")
            return None

    def update_discord_message_time(self, new_time_str):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config_content = file.read()
            config_content = re.sub(
                r'DiscordMessageTime\s*=\s*"\d{2}:\d{2}"',
                f'DiscordMessageTime = "{new_time_str}"',
                config_content
            )
            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                file.write(config_content)
            print(f"Updated DiscordMessageTime in {CONFIG_FILE} to {new_time_str}.")  # Only print, don't send to Telegram
        except Exception as e:
            self.log_to_telegram(f"Error while updating DiscordMessageTime: {e}")

    def save_config(self, date):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = file.read()
            formatted_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
            updated_config = re.sub(r'DiscordDate = "\d{2}-\d{2}-\d{4}"', f'DiscordDate = "{formatted_date}"', config)
            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                file.write(updated_config)
            print(f"Updated DiscordDate in {CONFIG_FILE} to {formatted_date}.")  # Only print, don't send to Telegram
        except Exception as e:
            self.log_to_telegram(f"Error while saving the configuration: {e}")

    def update_inventory(self, items_received):
        try:
            from balls import LIST

            # Create a dictionary for easy lookup (normalized names)
            inventory = {normalize_ball_name(ball["Name"]): ball for ball in LIST}

            # Update the stock for each received item
            for item_name, quantity in items_received.items():
                norm_item = normalize_ball_name(item_name)
                if norm_item in inventory:
                    inventory[norm_item]["Stock"] += quantity
                    self.log_to_telegram(f"Updated {inventory[norm_item]['Name']} stock to {inventory[norm_item]['Stock']}.")

            # Write the updated inventory back to balls.py
            with open("balls.py", "w", encoding="utf-8") as file:
                file.write("LIST = [\n")
                for ball in inventory.values():
                    file.write(f"    {ball},\n")
                file.write("]\n")

        except Exception as e:
            self.log_to_telegram(f"Error while updating inventory: {e}")

    def normalize_ball_name(name):
        return name.lower().replace(" ", "").replace("-", "")

    def is_auto_time_enabled(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = file.read()
            auto_time_match = re.search(r'DiscordAutoTime\s*=\s*(true|false)', config, re.IGNORECASE)
            if auto_time_match:
                return auto_time_match.group(1).lower() == "true"
        except Exception as e:
            self.log_to_telegram(f"Error while checking DiscordAutoTime: {e}")
        return False


# Erstellen und starten des Telegram-Bots
telegram_bot = TelegramBot()

if __name__ == "__main__":
    try:
        import discord
        client = SelfBot(telegram_bot=telegram_bot, chunk_guilds_at_startup=False)
        client.run(config.DiscordToken)  # Set bot=False for self-bot
    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
