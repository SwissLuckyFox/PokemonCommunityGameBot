import discord
import asyncio
import re
from datetime import datetime, timedelta
import random
from Telegram_Bot import TelegramBot  # Import Telegram Bot
import balls  # Import balls list
import ast  # To safely read Python list format

# Config file paths
CONFIG_FILE = "config.py"
BALLS_FILE = "balls.py"

class SelfBot(discord.Client):
    def __init__(self, telegram_bot, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(telegram_bot, TelegramBot):
            raise ValueError("TelegramBot instance is required but was not provided or initialized!")

        self.telegram_bot = telegram_bot
        self.balls = {ball["Name"].lower(): ball for ball in balls.LIST}  # Convert list to dictionary for easy lookup
        self.last_sent_date, self.bot_enabled, self.token, self.channel_id, self.message, self.fixed_time, self.max_delay = self.load_config()

    async def on_message(self, message):
        """Processes Discord messages to extract and log Pokéball rewards."""
        if message.channel.id != self.channel_id or message.author == self.user:
            return

        if "daily reward" in message.content.lower():
            extracted_balls = self.extract_pokeballs(message.content)
            if extracted_balls:
                self.update_ball_stock(extracted_balls)
                await self.send_balls_to_telegram(extracted_balls)
    def load_config(self):
        """Loads configuration values from config.py and ensures correct parsing."""
        try:
            with open(CONFIG_FILE, "r") as file:
                config = file.read()

                # Extracting values from config
                date_match = re.search(r'DiscordDate = "(\d{4}-\d{2}-\d{2})"', config)
                bot_match = re.search(r'BotDiscord = (true|false)', config, re.IGNORECASE)
                token_match = re.search(r'DiscordToken = "(.+?)"', config)
                channel_match = re.search(r'DiscordChannel = (\d+)', config)
                message_match = re.search(r'DiscordMessage = "(.+?)"', config)
                time_match = re.search(r'DiscordMessageTime = "(\d{2}:\d{2})"', config)
                delay_match = re.search(r'DiscordMessageDelay = "(\d+)"', config)

                last_date = date_match.group(1) if date_match else None
                bot_enabled = bot_match.group(1).lower() == "true" if bot_match else False
                token = token_match.group(1) if token_match else None
                channel_id = int(channel_match.group(1)) if channel_match else None
                message = message_match.group(1) if message_match else "!pokeda"

                # Load fixed time
                if time_match:
                    fixed_time = datetime.strptime(time_match.group(1), "%H:%M").time()
                else:
                    fixed_time = None

                # Load max delay
                max_delay = int(delay_match.group(1)) if delay_match else 0

                # Validate critical values
                if not bot_enabled:
                    print("Error: BotDiscord is set to false. Enable it in config.py")
                if not token:
                    print("Error: DiscordToken is missing.")
                if not channel_id:
                    print("Error: DiscordChannel is missing.")

                return last_date, bot_enabled, token, channel_id, message, fixed_time, max_delay

        except FileNotFoundError:
            print(f"Error: {CONFIG_FILE} not found.")
            return None, False, None, None, "!pokeda", None, 0


    def extract_pokeballs(self, message_text):
        """Extracts Pokéball rewards from a message."""
        ball_pattern = r"(\d+)x (\w+ball)"
        matches = re.findall(ball_pattern, message_text, re.IGNORECASE)

        extracted_balls = {}
        for count, ball_name in matches:
            normalized_name = ball_name.lower()
            if normalized_name in self.balls:
                extracted_balls[normalized_name] = extracted_balls.get(normalized_name, 0) + int(count)

        return extracted_balls

    def update_ball_stock(self, extracted_balls):
        """Updates the Pokéball stock in balls.py while preserving its original format."""
        # Load the current data from balls.py
        try:
            with open(BALLS_FILE, "r", encoding="utf-8") as f:
                content = f.read()
                data = ast.literal_eval(content.split("=", 1)[1].strip())  # Extract LIST from file
        except Exception as e:
            print(f"Error loading balls.py: {e}")
            return

        # Update stock values
        for ball in data:
            ball_name = ball["Name"].lower()
            if ball_name in extracted_balls:
                ball["Stock"] += extracted_balls[ball_name]

        # Write back to balls.py with the original format
        with open(BALLS_FILE, "w", encoding="utf-8") as f:
            f.write("LIST = [\n")
            for ball in data:
                f.write(f"    {{'Name': '{ball['Name']}', 'Stock': {ball['Stock']}}},\n")
            f.write("]\n")

    async def send_balls_to_telegram(self, extracted_balls):
        """Formats and sends Pokéball stock updates to Telegram."""
        message = "**🎉 New Pokéball Rewards! 🎉**\n"
        for ball_name, count in extracted_balls.items():
            message += f"🔹 **{ball_name.capitalize()}**: +{count}\n"

        await self.log_to_telegram(message)

    async def log_to_telegram(self, text):
        """Logs messages to Telegram asynchronously."""
        print(text)
        if self.telegram_bot:
            try:
                await self.telegram_bot.send_message(text)
            except Exception as e:
                print(f"Failed to send message to Telegram: {e}")


    async def on_ready(self):
        """Called when the bot is ready."""
        if not self.bot_enabled or not self.token or not self.channel_id:
            await self.log_to_telegram("The DiscordBot is disabled or not configured properly. Exiting...")

            # Close the bot properly to avoid unclosed session errors
            await self.close()
            return

        await self.log_to_telegram(f"Logged in as Discord User {self.user}")
        await self.schedule_daily_message()


    async def schedule_daily_message(self):
        """Schedules the daily message with a random delay."""
        if not self.fixed_time:
            await self.log_to_telegram("No valid time specified. Message scheduling skipped.")
            return

        today = datetime.now().date()
        if self.last_sent_date == today.strftime("%Y-%m-%d"):
            await self.log_to_telegram("The Discord message has already been sent today.")
            return

        # Calculate scheduled time
        fixed_time_today = datetime.combine(today, self.fixed_time)
        random_delay = random.randint(0, self.max_delay) * 60  # Convert minutes to seconds
        scheduled_time = fixed_time_today + timedelta(seconds=random_delay)

        # If scheduled time is already passed, move to next day
        now = datetime.now()
        if scheduled_time < now:
            scheduled_time += timedelta(days=1)

        delay_seconds = (scheduled_time - now).total_seconds()
        await self.log_to_telegram(f"Discord message scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}.")

        await asyncio.sleep(delay_seconds)
        await self.send_daily_message()

    async def send_daily_message(self):
        """Sends the daily message to the configured Discord channel."""
        channel = self.get_channel(self.channel_id)
        if channel is None:
            await self.log_to_telegram("Error: Discord Channel not found! Check DiscordChannel in config.")
            await self.schedule_daily_message()
            return

        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_sent_date == today:
            await self.log_to_telegram("The Discord message has already been sent today.")
            await self.schedule_daily_message()
            return

        try:
            await channel.send(self.message)
            await self.log_to_telegram(f"Discord Message sent: {self.message}")
            self.last_sent_date = today

            # Schedule next message after sending
            await self.schedule_daily_message()

        except Exception as e:
            await self.log_to_telegram(f"Error while sending Discord message: {e}")
            await self.schedule_daily_message()

    async def on_message(self, message):
        """Handles incoming messages to check for mentions or errors."""
        if message.channel.id != self.channel_id or message.author == self.user:
            return

        if message.mentions and self.user in message.mentions:
            if "You already have claimed your daily reward." in message.content:
                await self.log_to_telegram("Discord Message ignored: Daily reward already claimed.")
                return
            await self.log_to_telegram(f"Discord Message received: {message.content}")


# Start Telegram and Discord Bots
telegram_bot = TelegramBot()
if not telegram_bot:
    print("Error: Telegram bot failed to initialize!")

client = SelfBot(telegram_bot=telegram_bot, chunk_guilds_at_startup=False)
client.run(client.token)
