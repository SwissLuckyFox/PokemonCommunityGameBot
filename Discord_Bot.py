import discord
import asyncio
import re
from datetime import datetime, timedelta
import random
from Telegram_Bot import TelegramBot  # Importiere den Telegram-Bot

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

                date_match = re.search(r"DiscordDate = \"(\d{4}-\d{2}-\d{2})\"", config)
                bot_match = re.search(r"BotDiscord = (true|false)", config, re.IGNORECASE)
                token_match = re.search(r"DiscordToken = \"(.*?)\"", config)
                channel_match = re.search(r"DiscordChannel = (\d+)", config)
                message_match = re.search(r"DiscordMessage = \"(.*?)\"", config)
                username_match = re.search(r"DiscordUsername = \"(.*?)\"", config)
                timeframe_match = re.search(r"DiscordTimeframe = \"(\d{2}:\d{2})-(\d{2}:\d{2})\"", config)

                last_date = date_match.group(1) if date_match else None
                bot_enabled = bot_match.group(1).lower() == "true" if bot_match else False
                token = token_match.group(1) if token_match else None
                channel_id = int(channel_match.group(1)) if channel_match else None
                message = message_match.group(1) if message_match else "!pokeda"
                target_username = username_match.group(1) if username_match else ""

                if timeframe_match:
                    start_time = datetime.strptime(timeframe_match.group(1), "%H:%M")
                    end_time = datetime.strptime(timeframe_match.group(2), "%H:%M")
                    if end_time <= start_time:
                        end_time += timedelta(days=1)
                    timeframe = (start_time, end_time)
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
        print(text)  # Log to the console
        asyncio.create_task(self.telegram_bot.send_message(text))  # Send to Telegram

    async def on_ready(self):
        if not self.bot_enabled or not self.token or not self.channel_id:
            self.log_to_telegram("The DiscordBot is disabled or insufficiently configured. Exiting...")
            await self.close()
            return

        self.log_to_telegram(f"Logged in as Discord User {self.user}")
        await self.schedule_daily_message()

    async def schedule_daily_message(self):
        if not self.timeframe:
            self.log_to_telegram("No valid timeframe For Discord Message specified. The message will not be scheduled.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_sent_date == today:
            self.log_to_telegram("The Discord message has already been sent today.")
            return

        start_time, end_time = self.timeframe
        now = datetime.now()
        start_today = now.replace(hour=start_time.hour, minute=start_time.minute, second=0, microsecond=0)
        end_today = now.replace(hour=end_time.hour, minute=end_time.minute, second=0, microsecond=0)

        if now >= end_today:
            self.log_to_telegram("The current time is outside the specified Discord timeframe. The message will be scheduled for tomorrow.")
            start_today += timedelta(days=1)

        delay_seconds = (start_today - now).total_seconds()
        random_delay = random.randint(0, int((end_today - start_today).total_seconds()))

        self.log_to_telegram(f"The Discord message will be sent at {start_today + timedelta(seconds=random_delay)}.")
        await asyncio.sleep(delay_seconds + random_delay)
        await self.send_daily_message()

    async def send_daily_message(self):
        channel = self.get_channel(self.channel_id)
        if channel is None:
            self.log_to_telegram("Discord Channel not found! Please check the DiscordChannel in the config.py file.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_sent_date == today:
            self.log_to_telegram("The Discord message has already been sent today.")
            return

        try:
            await channel.send(self.message)
            self.log_to_telegram(f"Discord Message sent: {self.message}")
            self.last_sent_date = today
            self.save_config(today)
        except Exception as e:
            self.log_to_telegram(f"Error while sending the Discord message: {e}")

    async def on_message(self, message):
        if message.channel.id != self.channel_id or message.author == self.user:
            return

        if message.mentions and self.user in message.mentions:
            if "You already have claimed your daily reward." in message.content:
                self.log_to_telegram("Discord Message ignored: Daily reward already claimed.")
                return
            self.log_to_telegram(f"Discord Message received: {message.content}")


# Erstellen und starten des Telegram-Bots
telegram_bot = TelegramBot()

# Erstellen und starten des Discord-Bots
client = SelfBot(telegram_bot=telegram_bot, chunk_guilds_at_startup=False)
client.run(client.token)
