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
                fixed_time = datetime.strptime(time_match.group(1), "%H:%M").time() if time_match else None

                # Load max delay
                max_delay = int(delay_match.group(1)) if delay_match else 0

                return last_date, bot_enabled, token, channel_id, message, fixed_time, max_delay

        except FileNotFoundError:
            print(f"Error: {CONFIG_FILE} not found.")
            return None, False, None, None, "!pokeda", None, 0

    async def on_ready(self):
        """Called when the bot is ready."""
        if not self.bot_enabled or not self.token or not self.channel_id:
            await self.log_to_telegram("The DiscordBot is disabled or not configured properly. Exiting...")
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
            await self.log_to_telegram("The Discord message has already been sent today. Scheduling for tomorrow.")
            today += timedelta(days=1) 

        # Calculate scheduled time with random delay
        fixed_time_today = datetime.combine(today, self.fixed_time)
        random_delay_minutes = random.randint(0, self.max_delay)
        random_delay_seconds = random.randint(0, 59)
        scheduled_time = fixed_time_today + timedelta(minutes=random_delay_minutes, seconds=random_delay_seconds)

        now = datetime.now()
        if scheduled_time < now:
            scheduled_time += timedelta(days=1)

        delay_seconds = (scheduled_time - now).total_seconds()
        await self.log_to_telegram(f"Discord message scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}.")

        await asyncio.sleep(delay_seconds)
        await self.send_daily_message()

        # Calculate scheduled time with random delay
        fixed_time_today = datetime.combine(today, self.fixed_time)
        random_delay_minutes = random.randint(0, self.max_delay)
        random_delay_seconds = random.randint(0, 59)
        scheduled_time = fixed_time_today + timedelta(minutes=random_delay_minutes, seconds=random_delay_seconds)

        # If scheduled time is already passed today, move to next day
        now = datetime.now()
        if scheduled_time < now:
            scheduled_time += timedelta(days=1)

        delay_seconds = (scheduled_time - now).total_seconds()
        await self.log_to_telegram(f"Discord message scheduled for {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}.")

        await asyncio.sleep(delay_seconds)
        await self.send_daily_message()

    async def send_daily_message(self):
        """Send the daily message to the configured Discord channel."""
        channel = self.get_channel(self.channel_id)
        if channel is None:
            await self.log_to_telegram("Error: Discord channel not found! Check DiscordChannel in config.py.")
            return

        today = datetime.now().strftime("%Y-%m-%d")

        if self.last_sent_date == today:
            await self.log_to_telegram("Already sent daily Discord message.")
            return

        try:
            await channel.send(self.message)
            await self.log_to_telegram(f"Discord message sent: {self.message}")

            # ✅ Save the new date BEFORE scheduling the next message
            self.save_last_sent_date(today)
            self.last_sent_date = today  # ✅ Ensure the new date is in memory

            # ✅ Now schedule the next message after saving the date
            await self.schedule_daily_message()

        except Exception as e:
            await self.log_to_telegram(f"Failed to send the Discord message: {e}")



    def save_last_sent_date(self, date):
        """Saves the last sent date in the configuration file."""
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                config = file.read()

            updated_config = re.sub(r'DiscordDate = "\d{4}-\d{2}-\d{2}"', f'DiscordDate = "{date}"', config)

            with open(CONFIG_FILE, "w", encoding="utf-8") as file:
                file.write(updated_config)

            self.last_sent_date = date

        except Exception as e:
            print(f"Error saving the last sent date: {e}")

    async def log_to_telegram(self, text):
        """Logs messages to Telegram asynchronously."""
        print(text)
        if self.telegram_bot:
            try:
                await self.telegram_bot.send_message(text)
            except Exception as e:
                print(f"Failed to send message to Telegram: {e}")

# Start Telegram and Discord Bots
telegram_bot = TelegramBot()
if not telegram_bot:
    print("Error: Telegram bot failed to initialize!")

client = SelfBot(telegram_bot=telegram_bot, chunk_guilds_at_startup=False)
client.run(client.token)
