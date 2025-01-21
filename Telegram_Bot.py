import asyncio
import importlib
import json  # Import the JSON library for pretty-printing
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import config  # Direct access to configuration values
import balls  # Direct access to the ball list


class TelegramBot:
    def __init__(self):
        self.bot = Bot(token=config.TelegramBotToken)
        self.dispatcher = Dispatcher()

        # Register command handlers
        self.dispatcher.message.register(self.process_command)

    def reload_modules(self):
        """
        Reloads config.py and balls.py to apply changes dynamically.
        """
        importlib.reload(config)
        importlib.reload(balls)

    def save_balls(self):
        """
        Saves the ball list to balls.py in a nicely formatted way.
        """
        with open("balls.py", "w") as file:
            file.write("LIST = [\n")
            for ball in balls.LIST:
                file.write(f"    {ball},\n")
            file.write("]\n")

    def save_config(self):
        """
        Updates config.py with the current state of the config object.
        """
        with open("config.py", "w") as file:
            for key in dir(config):
                if key.startswith("__"):
                    continue
                value = getattr(config, key)
                if isinstance(value, dict):
                    value = json.dumps(value, indent=4)
                elif isinstance(value, str):
                    value = f'"{value}"'
                file.write(f"{key} = {value}\n")

    def find_ball(self, ball_name: str):
        """
        Finds a ball in the list.
        """
        for ball in balls.LIST:
            if ball["Name"].lower() == ball_name.lower():
                return ball
        return None

    async def process_command(self, message: Message):
        """
        Processes messages that start with '!' and routes them to the correct handler.
        """
        if not message.text.startswith("!"):
            # Ignore messages that do not start with '!'
            return

        # Remove '!' and split the message into parts
        parts = message.text[1:].strip().split(maxsplit=1)

        if len(parts) < 1:
            await message.answer("Invalid format. Use the !Commands command to see the correct usage.")
            return

        command = parts[0].lower()  # Normalize command to lowercase
        args = parts[1] if len(parts) > 1 else ""

        try:
            if command == "commands":
                commands_list = (
                    "Available commands:\n"
                    "!ShowStock <ball_name|All> - View stock of a specific ball or all balls.\n"
                    "!AddBall <ball_name> <amount> - Add a specified number of balls.\n"
                    "!RemoveBall <ball_name> <amount> - Remove a specified number of balls.\n"
                    "!SetStock <ball_name> <amount> - Set the stock of a specific ball.\n"
                    "!Show <config_key> - Show the value of a configuration key.\n"
                    "!Set <config_key>=<value> - Set the value of a configuration key.\n"
                    "!Set Timeframe <day> start: <HHMM> end: <HHMM> interval min <min> max <max> - Update the timeframe for a specific day.\n"
                    "!Show Timeframes - Display all timeframes in a friendly format.\n"
                    "!ConfigKeys - List all possible configuration keys."
                )
                await message.answer(commands_list)

            elif command == "configkeys":
                # Dynamically list all keys in the config module
                config_keys = [key for key in dir(config) if not key.startswith("__")]
                response = "Available configuration keys:\n" + "\n".join(config_keys)
                await message.answer(response)

            elif command == "show":
                # Handle !Show <config_key>
                if not args:
                    await message.answer("Please specify a configuration key to show. Example: !Show TelegramBotToken")
                    return

                config_key = args.strip()
                if hasattr(config, config_key):
                    value = getattr(config, config_key)
                    if isinstance(value, dict):
                        value = json.dumps(value, indent=4)
                    await message.answer(f"{config_key}:\n{value}")
                else:
                    await message.answer(f"Config key '{config_key}' not found. Use !ConfigKeys to see available keys.")

            elif command == "set":
                if not "=" in args:
                    await message.answer("Unknown Set Command. Example: !Set Income=900")
                else:
                    # Existing logic for parsing and updating the config key
                    try:
                        config_key, value = map(str.strip, args.split("=", 1))
                        if hasattr(config, config_key):
                            current_value = getattr(config, config_key)
                            # Convert value to the correct type
                            if isinstance(current_value, bool):
                                value = value.lower() in ["true", "1", "yes"]
                            elif isinstance(current_value, int):
                                value = int(value)
                            elif isinstance(current_value, float):
                                value = float(value)
                            elif isinstance(current_value, dict):
                                value = json.loads(value)
                            else:
                                value = str(value)

                            setattr(config, config_key, value)
                            self.save_config()
                            await message.answer(f"Config key '{config_key}' updated to: {value}")
                        else:
                            await message.answer(f"Config key '{config_key}' not found. Use !ConfigKeys to see available keys.")
                    except Exception as e:
                        await message.answer(f"Failed to update config key: {str(e)}")

            elif command == "showstock":
                if not args:
                    await message.answer("Please provide a ball name or 'All'. Example: !ShowStock All")
                    return
                await self.show_stock(message, args)

            elif command == "addball":
                args_split = args.split(maxsplit=1)
                if len(args_split) < 2 or not args_split[1].isdigit():
                    await message.answer("Invalid format. Example: !AddBall <ball_name> <amount>")
                    return
                ball_name = args_split[0]
                amount = int(args_split[1])
                await self.add_ball(message, ball_name, amount)

            elif command == "removeball":
                args_split = args.split(maxsplit=1)
                if len(args_split) < 2 or not args_split[1].isdigit():
                    await message.answer("Invalid format. Example: !RemoveBall <ball_name> <amount>")
                    return
                ball_name = args_split[0]
                amount = int(args_split[1])
                await self.remove_ball(message, ball_name, amount)

            elif command == "setstock":
                args_split = args.split(maxsplit=1)
                if len(args_split) < 2 or not args_split[1].isdigit():
                    await message.answer("Invalid format. Example: !SetStock <ball_name> <amount>")
                    return
                ball_name = args_split[0]
                amount = int(args_split[1])
                await self.set_stock(message, ball_name, amount)

            elif command == "show":
                if args.lower() == "timeframes":
                    await self.show_timeframes(message)
                else:
                    await message.answer("Unknown key. Use the !Commands command to see available keys.")

            else:
                await message.answer("Unknown command. Use the !Commands command to see available commands.")

        except Exception as e:
            await message.answer(f"An error occurred: {str(e)}")

    async def show_timeframes(self, message: Message):
        response = "Timeframes:\n"
        for day, data in config.timeframes.items():
            response += (
                f"{day}: Start {data['start']}, End {data['end']}, "
                f"Random Interval: Min {data['random_interval']['min']}, Max {data['random_interval']['max']}\n"
            )
        await message.answer(response)

    async def show_stock(self, message: Message, ball_name: str):
        if ball_name.lower() == "all":
            response = "Stock for all balls:\n"
            for ball in balls.LIST:
                response += f"{ball['Name']}: {ball['Stock']}\n"
            await message.answer(response)
        else:
            ball = self.find_ball(ball_name)
            if ball:
                await message.answer(f"{ball['Name']} stock: {ball['Stock']}")
            else:
                await message.answer(f"Sorry, {ball_name} not found.")

    async def add_ball(self, message: Message, ball_name: str, amount: int):
        ball = self.find_ball(ball_name)
        if ball:
            ball["Stock"] += amount
            self.save_balls()
            await message.answer(f"Added {amount} {ball_name}. New stock: {ball['Stock']}")
        else:
            await message.answer("Sorry. Ball not found.")

    async def remove_ball(self, message: Message, ball_name: str, amount: int):
        ball = self.find_ball(ball_name)
        if ball:
            removed_amount = min(ball["Stock"], amount)
            ball["Stock"] -= removed_amount
            self.save_balls()
            await message.answer(f"Removed {removed_amount} {ball_name}. New stock: {ball['Stock']}")
        else:
            await message.answer("Sorry. Ball not found.")

    async def set_stock(self, message: Message, ball_name: str, amount: int):
        ball = self.find_ball(ball_name)
        if ball:
            if amount >= 0:
                ball["Stock"] = amount
                self.save_balls()
                await message.answer(f"Stock of {ball_name} has been set to {amount}.")
            else:
                await message.answer("The amount cannot be below 0.")
        else:
            await message.answer("Sorry. Ball not found.")

    async def send_message(self, text: str):
        await self.bot.send_message(chat_id=config.TelegramChatID, text=text)

    async def run(self):
        print("Telegram bot is starting...")
        await self.dispatcher.start_polling(self.bot)


if __name__ == "__main__":
    if not config.UseTelegram:
        print("Telegram bot is disabled. Set UseTelegram = True in the config.py file to enable it.")
    else:
        bot = TelegramBot()

        async def main():
            await bot.run()

        asyncio.run(main())
