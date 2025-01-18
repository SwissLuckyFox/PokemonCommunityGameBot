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
        Saves the ball list to balls.py.
        """
        with open("balls.py", "w") as file:
            file.write(f"LIST = {balls.LIST}")

    def save_config(self):
        """
        Replaces the timeframes section in config.py without duplicating or corrupting the rest of the file.
        """
        with open("config.py", "r") as file:
            lines = file.readlines()

        # Locate the start and end of the timeframes block
        start_idx = None
        end_idx = None
        for idx, line in enumerate(lines):
            if line.strip().startswith("timeframes ="):
                start_idx = idx
            elif start_idx is not None and line.strip() == "    },":
                end_idx = idx
                break

        if start_idx is None or end_idx is None:
            raise ValueError("The timeframes block was not found in config.py.")

        # Debugging: Show indices
        print(f"Debug: start_idx = {start_idx}, end_idx = {end_idx}")

        # Format the updated timeframes block
        updated_timeframes = "timeframes = " + json.dumps(config.timeframes, indent=4) + ",\n"
        # Debugging: Log the updated block
        print(f"Debug: Writing updated timeframes block:\n{updated_timeframes}")

        # Replace the timeframes block
        new_lines = lines[:start_idx] + [updated_timeframes] + lines[end_idx + 1:]

        with open("config.py", "w") as file:
            file.writelines(new_lines)


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
        Processes all commands starting with '!'.
        """
        if not message.text.startswith("!"):
            return

        # Remove '!' and split the message into parts
        parts = message.text[1:].strip().split(maxsplit=1)

        if len(parts) < 1:
            await message.answer("Invalid format. Please check your command.")
            return

        command = parts[0]

        try:
            if command == "Commands":
                commands_list = (
                    "Available commands:\n"
                    "!SeeStock <ball_name|All> - View stock of a specific ball or all balls.\n"
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
            elif command == "SeeStock":
                if len(parts) == 2:
                    await self.see_stock(message, parts[1])
                else:
                    await message.answer("Invalid format. Example: !SeeStock Netball or !SeeStock All")
            elif command in ["AddBall", "RemoveBall", "SetStock"]:
                if len(parts) != 2:
                    await message.answer("Invalid format. Example: !AddBall Netball 10")
                    return

                subparts = parts[1].split()
                if len(subparts) != 2:
                    await message.answer("Invalid format. Example: !AddBall Netball 10")
                    return

                ball_name, amount = subparts[0], int(subparts[1])

                if command == "AddBall":
                    await self.add_ball(message, ball_name, amount)
                elif command == "RemoveBall":
                    await self.remove_ball(message, ball_name, amount)
                elif command == "SetStock":
                    await self.set_stock(message, ball_name, amount)
            elif command == "Show":
                if len(parts) < 2:
                    await message.answer("Invalid format. Example: !Show TimerBallTime")
                    return

                key = parts[1].strip()
                if key.lower() == "timeframes":
                    await self.show_timeframes(message)
                elif hasattr(config, key):
                    value = getattr(config, key)
                    await message.answer(f"{key} = {value}")
                else:
                    await message.answer(f"'{key}' is not a valid configuration key.")
            elif command == "ConfigKeys":
                keys = [key for key in dir(config) if not key.startswith("_")]
                response = "Available configuration keys:\n" + "\n".join(keys)
                await message.answer(response)
            elif command == "Set" and parts[1].startswith("Timeframe"):
                subparts = parts[1].replace(":", "").split()
                if len(subparts) < 10:
                    await message.answer("Invalid format. Example: !Set Timeframe Monday start: 2230 end: 2330 interval min 15 max 30")
                    return

                day = subparts[1]
                if day not in config.timeframes:
                    await message.answer("Invalid day. Please use a valid weekday like Monday, Tuesday, etc.")
                    return

                try:
                    # Convert time to HH:MM format
                    start = f"{subparts[3][:2]}:{subparts[3][2:]}"  # Converts 2230 -> 22:30
                    end = f"{subparts[5][:2]}:{subparts[5][2:]}"    # Converts 2330 -> 23:30
                    min_interval = int(subparts[8])
                    max_interval = int(subparts[10])

                    config.timeframes[day] = {
                        "start": start,
                        "end": end,
                        "random_interval": {
                            "min": min_interval,
                            "max": max_interval
                        }
                    }

                    self.save_config()
                    await message.answer(f"Timeframe for {day} updated: Start {start}, End {end}, Interval Min {min_interval}, Max {max_interval}.")
                except ValueError:
                    await message.answer("Invalid interval values. Please ensure min and max are numbers.")
            else:
                await message.answer("Unknown command. Please check your input.")

        except ValueError:
            await message.answer("Invalid format. Please check your input.")

    async def show_timeframes(self, message: Message):
        response = "Timeframes:\n"
        for day, data in config.timeframes.items():
            response += (
                f"{day}: Start {data['start']}, End {data['end']}, "
                f"Random Interval: Min {data['random_interval']['min']}, Max {data['random_interval']['max']}\n"
            )
        await message.answer(response)

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
