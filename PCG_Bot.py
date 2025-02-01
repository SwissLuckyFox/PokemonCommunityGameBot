#!/usr/bin/env python
import socket
import ssl
import datetime
import random
import time
import pokemon
import balls
import re
from collections import namedtuple
from config import timeframes, AutoCatch
import config
import requests
import importlib

def on_message_receive(bot, message):

    utc_time = datetime.utcnow()
    msg_time = utc_time.strftime("%Y-%m-%d %H:%M:%S (UTC)")
    msg_text = message["text"]
    bot.send_message("Pong")
    print(msg_time, msg_text)

    # Watch if its time to Start with a randome leeway.      
def wait_if_not_in_timeframe(self, timeframes):
    now = datetime.datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    start_time = timeframes[current_day]["start"]
    end_time = timeframes[current_day]["end"]

    if start_time <= end_time:
        # Normal case: end time is after start time
        in_timeframe = start_time <= current_time <= end_time
    else:
        # Wrapped case: end time is before start time
        in_timeframe = start_time <= current_time or current_time <= end_time

    if not in_timeframe:
        # Calculate time difference in seconds
        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M")
        current_time_obj = datetime.datetime.strptime(current_time, "%H:%M")
        time_diff = (start_time_obj - current_time_obj).seconds

        # Generate a random interval within the given min and max
        random_interval_min = timeframes[current_day]["random_interval"]["min"]
        random_interval_max = timeframes[current_day]["random_interval"]["max"]
        random_interval = random.randint(random_interval_min, random_interval_max) * 60  # convert to seconds

        # Add the random interval to the time difference
        wait_time = time_diff + random_interval
        wait_time_Format = wait_time // 60
        wait_date = (now + datetime.timedelta(seconds=wait_time)).strftime("%H:%M")
        print(
            f"Still Sleeping for {wait_time_Format} minutes. Will start again at {wait_date}."
        )
        self.send_Telegram_msg(
            f"Still Sleeping for {wait_time_Format} minutes. Will start again at {wait_date}."
        )
        time.sleep(wait_time)
        print(f"Ring! Ring! Sleeptime is over!")
        self.send_Telegram_msg(f"Ring! Ring! Sleeptime is over!")
        self.connect()
        
        return False
    else:
        return True
    
Message = namedtuple(
    "Message",
    "prefix user channel irc_command irc_args text text_command text_args",
)

def remove_prefix(string, prefix):
    if not string.startswith(prefix):
        return string
    return string[len(prefix) :]
  
# Generate a random number in secounds
def wait_random_time(Bot):
    Bot.reload_modules()
    random_time = random.randint(config.RandomeFrom, config.RandomeTo)
    print(f"Wait for {random_time} secounds.")
    if config.ShowRandomeTime:
        Bot.send_Telegram_msg(f"Wait for {random_time} secounds.")
        time.sleep(random_time)

class Bot:
    def __init__(self):
        self.irc_server = config.irc_server
        self.irc_port = config.irc_port
        self.oauth_token = config.OAUTH_TOKEN
        self.username = config.Username
        self.channels = config.Channels
        self.PokeBot = config.Pokemonbot.lower()
        self.command_prefix = "@"
        self.UseBall = config.BallToBuy
        self.time_needed = datetime.datetime.now()
        self.WaitForMoney = bool(False)                    
        self.Missed = bool(False)
        self.last_recommendation_time = 0
        self.cooldown_duration = 100
        self.success = False
        self.BuyBall = config.BallToBuy
        self.response_msg = "Done"
        self.RecoBall = None
        self.CatchEmote = config.CatchEmote
        self.HowMany = config.HowMany
        self.UseRecommended = config.UseRecommended
        self.AutoBall = config.AutoBall
        self.UsedBall = []
    def reload_modules(self):
        importlib.reload(config)
        importlib.reload(balls)

    def init(self):
        self.connect()

    def send_privmsg(self, channel, text):
        self.send_command(f"PRIVMSG #{channel} :{text}")

    def send_command(self, command):
        self.irc.send((command + "\r\n").encode())
        # if 'PASS' not in command:
        # print(f'< {command}')

    def connect(self):
        while True:
                    try:
                        self.irc = ssl.wrap_socket(socket.socket())
                        self.irc.connect((self.irc_server, self.irc_port))
                        self.send_command(f"PASS {self.oauth_token}")
                        self.send_command(f"NICK {self.username}")
                        for channel in self.channels:
                            self.send_command(f"JOIN #{channel}")
                            print(
                                f"{self.username} is going to {channel}`s Safarizone to Catch some Pokemon!"
                            )
                            self.send_Telegram_msg(
                                f"{self.username} is going to {channel}`s Safarizone to Catch some Pokemon!"
                            )
                        self.loop_for_messages()
                    except (OSError, socket.error, ssl.SSLError) as e:
                        print(f"Error during connection: {e}")
                        time.sleep(10)  # Wait for 10 seconds before retrying
        
    def get_user_from_prefix(self, prefix):
        domain = prefix.split("!")[0]
        if domain.endswith(".tmi.twitch.tv"):
            return domain.replace(".tmi.twitch.tv", "")
        if "tmi.twitch.tv" not in domain:
            return domain
        return None

    # Splitting Message into parts to Filter it more easely
    def parse_message(self, received_msg):
        parts = received_msg.split(" ")

        prefix = None
        user = None
        channel = None
        text = None
        text_command = None
        text_args = None
        irc_command = None
        irc_args = None

        if parts[0].startswith(":"):
            prefix = remove_prefix(parts[0], ":")
            user = self.get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(":")), None
        )
        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = " ".join(text_parts)
            if text_parts[0].startswith(self.command_prefix):
                text_command = remove_prefix(text_parts[0], self.command_prefix)
                text_args = text_parts[1:]
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith("#")), None
        )
        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        message = Message(
            prefix=prefix,
            user=user,
            channel=channel,
            text=text,
            text_command=text_command,
            text_args=text_args,
            irc_command=irc_command,
            irc_args=irc_args,
        )
        return message
    
    #Randome time to ignore Catch messages.
    def should_miss(self):
        miss_percentage = config.MissPercentage
        random_number = random.randint(1, 100)
        self.Miss = random_number <= miss_percentage
        return self.Miss

    #Calculate the time it needs to get the desired balance
    def CalculateTimeNeed(self, NeededMoney, Balance, Income,):
        self.WaitForMoney = bool(True)
        hours_needed = (NeededMoney - Balance) / Income
        self.time_needed = datetime.datetime.now() + datetime.timedelta(hours=hours_needed)
        self.Calculatet_Time = datetime.datetime.now() >= self.time_needed
        self.formatted_time = self.time_needed.strftime("%H:%M")
        print(
            f"I have {Balance}$. I need {NeededMoney}$. My income is {Income}$."
            )
        print(
            f"Will not catch until {self.formatted_time}. Need Money to buy Balls"
            )
        self.send_Telegram_msg(
            f"I have {Balance}$. I need {NeededMoney}$. My income is {Income}$."
            )
        self.send_Telegram_msg(
            f"Will not catch until {self.formatted_time}. Need Money to buy Balls"
            )
        return self.time_needed, self.Calculatet_Time, self.formatted_time
    
    #Chat handeling stuff
    def handle_message(self, received_msg):
        wait_if_not_in_timeframe(self, timeframes)
        if len(received_msg) == 0:
            return
        master = config.Pokemonbot.lower()
        message = self.parse_message(received_msg)
        #print(f'> {message}')
        trainer = self.username
        BuyBall = config.BallToBuy
        HowMany = config.HowMany
        UserLow = config.Username.lower()
        Emote = config.Emote
        CatchEmote = config.CatchEmote
        # Filter Messanges and throws Balls according to pokemon.py file
        if message.user == master and message.text is not None:
            if wait_if_not_in_timeframe(self, timeframes):
                if "Catch it using !pokecatch" in message.text:
                    self.reload_modules()
                    self.Calculatet_Time = datetime.datetime.now() >= self.time_needed    
                    # Iterate over the Pokemon list
                    for pokemon_data in pokemon.LIST:
                        self.pokemon_name = pokemon_data["Name"]
                        if pokemon_data["Name"].lower() in message.text.lower():
                            self.recommended_Balls = pokemon_data["UseBalls"].split() if pokemon_data["UseBalls"] else []
                            self.UseBall = self.recommended_Balls
                            self.auto_catch = pokemon_data["AllowSkip"]
                            self.pokemon_name = pokemon_data["Name"]
                            self.DexNr = pokemon_data["DexNr"]
                            self.can_catch = pokemon_data["Catch"]
                            if self.can_catch:
                                if self.pokemon_name in message.text:
                                    self.Missed = False
                                    self.WaitForMoney = False
                                    self.recommended_Balls = pokemon_data["UseBalls"].split() if pokemon_data["UseBalls"] else []
                                    print(f"It's a {self.pokemon_name}! DexNr: {self.DexNr}!")
                                    self.send_Telegram_msg(f"It's a {self.pokemon_name}!")
                                    if self.can_catch:
                                        if self.recommended_Balls != []:
                                            print("ListNotreco")
                                            self.ThrowBall(received_msg)
                                        elif not self.UseRecommended:
                                            print("Notreco")
                                            self.ThrowBall(received_msg)
                                    
                                        elif self.UseRecommended:
                                            print(f"Wait for Deemonriders Recommendations")
                                            self.send_Telegram_msg(f"Wait for Deemonriders Recommendations")


                                    else:  # Sends emote if Pokemon shouldn"t be caught
                                        self.Missed = True
                                        print(f"""A {self.pokemon_name}... I'll Pass on that!""")
                                        self.send_Telegram_msg(f"""A {self.pokemon_name}... I'll Pass on that!""")
                                        random_time = random.randint(50, 70)
                                        time.sleep(random_time)
                                        self.send_privmsg(message.channel, Emote)
                                        print(f"Send {Emote} to collect money!") 
                                        self.send_Telegram_msg(f"Send {Emote} to collect money!")
                            else:
                                if self.pokemon_name in message.text:
                                    self.Missed = True
                                    print("Missed the catch on purpose!")  
                                    self.send_Telegram_msg("Missed the catch on purpose!")
   
                #Try to buy balls  
                elif """You don't own that ball. Check the extension to see your items""" in message.text:
                    if f'@{trainer}' in message.text:
                        if self.UsedBall == []:
                            self.UsedBall = self.BuyBall
                        self.UseBall = self.recommended_Balls[0]
                        self.response_msg = message.text
                        if self.UsedBall != self.BuyBall:
                            self.ThrowBall(received_msg)

                elif "Deemon recommends:" in message.text and self.UseRecommended:
                    print("UseDeemon")
                    if not self.UseBall:
                        current_time = time.time()  # Get the current time
                        # Check if enough time has passed since the last recommendation
                        if current_time - self.last_recommendation_time >= self.cooldown_duration:
                            self.last_recommendation_time = current_time  # Update the last recommendation time
                            recommended_balls_text = message.text.split("Deemon recommends:")[1].strip()  # Extract recommended balls text
                            self.send_Telegram_msg(f"{recommended_balls_text}")
                            # Split the recommended balls text based on spaces to handle each word separately
                            recommended_balls_words = recommended_balls_text.split()
                            # Filter valid balls from each word
                            self.recommended_Balls = []
                            for word in recommended_balls_words:
                                for pokeball_data in balls.LIST:
                                    if word.strip() == pokeball_data["Name"]:
                                        self.recommended_Balls.append(word.strip())
                            if self.recommended_Balls:
                                self.UseBall = self.recommended_Balls[0]
                            else:  # If no valid balls found, use default ball
                                self.UseBall = self.BuyBall
                            self.ThrowBall(received_msg)
                        #else:
                            #print("Recommendations are on cooldown. Skipping...")
                            #self.send_Telegram_msg("Recommendations are on cooldown. Skipping...")

                #Try to throw after Purchase   
                elif "Purchase successful" in message.text:
                    if f"@{trainer}" in message.text:
                        for pokeball_data in balls.LIST:
                            if pokeball_data["Name"] == self.BuyBall:
                                pokeball_data["Stock"] += (int(self.HowMany) - 1)
                                with open("balls.py", "w") as f:
                                    f.write("LIST = [\n")
                                    for pokeball_data in balls.LIST:
                                        f.write(f"    {pokeball_data},\n")
                                    f.write("]")
                        if BuyBall != ["Pokeball"]:
                            print(f"Bought {HowMany} {BuyBall}s")
                            self.send_Telegram_msg(f"Bought {HowMany} {BuyBall}s")
                            wait_random_time(self)
                            self.send_privmsg(message.channel, f'{CatchEmote} {BuyBall}')
                            print(f"Throw {BuyBall}")
                            self.send_Telegram_msg(f"Throw {BuyBall}")
                            self.UsedBall = BuyBall
                        elif BuyBall == ["Pokeball"]:
                            print(f"Bought {HowMany} {BuyBall}s")
                            self.send_Telegram_msg(f"Bought {HowMany} {BuyBall}s")
                            wait_random_time(self)
                            self.send_privmsg(message.channel, CatchEmote)
                            print(f"Throw {BuyBall}")
                            self.send_Telegram_msg(f"Throw {BuyBall}")
                            self.UsedBall = BuyBall
                            
                #Look for failed purachase               
                elif f"""You don't have enough""" in message.text:
                    if f"@{trainer}" in message.text:
                        match = re.search(r'\D*(\d+)', message.text)
                        if match:
                            self.NeededMoney = int(match.group(1))
                            print(f"You need {int(match.group(1))} Pokedollers")
                            wait_random_time(self)
                            self.send_privmsg(message.channel, "!pokepass")
                            print("Get Balance")
                            self.send_Telegram_msg("Get Balance")
                            
                #Check if catched       
                elif "has been caught by:" in message.text:
                    if not self.Missed:
                        if AutoCatch:
                            if not self.WaitForMoney:
                                if UserLow in message.text:
                                    print("Catched it! =D")
                                    self.send_Telegram_msg("Catched it! =D")
                                else:
                                    print("It broke out! =(")
                                    self.send_Telegram_msg("It broke out! =(")
                elif "No one caught it." in message.text:
                    if not self.Missed:
                        if AutoCatch:
                            if not self.WaitForMoney:
                                print("It broke out! =(")
                                self.send_Telegram_msg("It broke out! =(")
                
                #Gets the Balance and starts Calculation
                elif "Balance" in message.text:
                    if trainer in message.text:
                        match = re.search(r'\$(\d+)', message.text)
                        if match:
                            self.Income = config.Income 
                            self.Balance = int(match.group(1))
                            #print(f'Your balance is {int(match.group(1))}')
                            self.CalculateTimeNeed(self.NeededMoney, self.Balance, self.Income)     
                
                #Cristmas event stuff
                elif "A christmas Delibird appeared!" in message.text:
                    print("A christmas Delibird appeared")
                    self.send_Telegram_msg("A christmas Delibird appeared!")
                    wait_random_time(self)
                    self.send_privmsg(message.channel, "Nice")
                    print("Was nice this year.")
                    self.send_Telegram_msg("Was nice this year.")

        # Ping Pong with Twitch
        if message.irc_command == "PING":
            self.send_command("PONG :tmi.twitch.tv")
            #print('Ping Pong Twitch')

        #Resume Autocatch with Codeword
        if message.user == UserLow and message.text is not None:
            if config.CodewordStart in message.text:
                self.AutoCatch = True
                print("Resume Autocatch")
                self.send_Telegram_msg("Resume Autocatch")
            if config.CodewordStop in message.text:
                self.AutoCatch = False
                print("Stop Autocatch")
                self.send_Telegram_msg("Stop Autocatch") 

    def select_ball_to_use(self):
        for recommended_ball in self.recommended_Balls:
            for pokeball_data in balls.LIST:
                if pokeball_data["Name"] == recommended_ball:
                    if pokeball_data["Stock"] > 0:
                        return recommended_ball  # Return the first available recommended ball
        return self.BuyBall  # If no recommended balls are available, return the default ball

    def ThrowBall(self, received_msg):
            self.reload_modules()
            message = self.parse_message(received_msg)
            print(self.recommended_Balls)
            
            if self.should_miss:
                if self.Calculatet_Time:
                    self.UseBall = self.select_ball_to_use()
                    # Iterate over each ball in the list
                    for pokeball_data in balls.LIST:
                        self.PokeballName = pokeball_data["Name"]
                        self.PokeballStock = pokeball_data["Stock"]
                        
                        if self.PokeballName == self.UseBall:
                            if self.PokeballStock > 0:  # Check if the ball is in stock
                                pokeball_data["Stock"] -= 1  # Decrement stock count
                                with open("balls.py", "w") as f:
                                    f.write("LIST = [\n")
                                    for pokeball_data in balls.LIST:
                                        f.write(f"    {pokeball_data},\n")
                                    f.write("]")
                                
                                # Throw logic based on the type of ball
                                if self.PokeballName == "Pokeball":
                                    wait_random_time(self)
                                    print(f"Throw {self.UseBall}!")
                                    self.send_Telegram_msg(f"Throw {self.UseBall}!")
                                    self.send_privmsg(message.channel, f'{self.CatchEmote}')
                                    self.UsedBall = self.UseBall
                                    return

                                elif self.UseBall == "Fastball":
                                    print("Fastball! Throw Fast!")
                                    self.send_Telegram_msg("Quickball! Throw Fast!")
                                    self.send_privmsg(message.channel, f'{self.CatchEmote} {self.UseBall}')
                                    self.UsedBall = self.UseBall
                                    return

                                elif self.UseBall == "Timerball":
                                    print(f"It's a Timerball. Slowpoke time! Wait for {config.TimerBallTime}")
                                    self.send_Telegram_msg(f"It's a Timerball. Slowpoke time! Wait for {config.TimerBallTime}")
                                    time.sleep(config.TimerBallTime)
                                    print(f"Throw {self.UseBall}")
                                    self.send_Telegram_msg(f"Throw {self.UseBall}")
                                    self.send_privmsg(message.channel, f'{self.CatchEmote} {self.UseBall}')
                                    self.UsedBall = self.UseBall
                                    return

                                else:
                                    wait_random_time(self)
                                    print(f"Throw {self.UseBall}")
                                    self.send_Telegram_msg(f"Throw {self.UseBall}")
                                    self.send_privmsg(message.channel, f'{self.CatchEmote} {self.UseBall}')
                                    self.UsedBall = self.UseBall
                                    return

                            # If the selected ball is not in stock, try again with the default ball
                            if self.UseBall != self.BuyBall:
                                print(f"No Usable Ball on Stock. Use {self.BuyBall}")
                                self.send_Telegram_msg(f"No Usable Ball on Stock. Use {self.BuyBall}")
                                self.UseBall = self.BuyBall
                                self.ThrowBall(received_msg)  
                            
                            if self.UseBall ==  self.BuyBall:
                                print(f"No {self.BuyBall} on Stock. Try to buy {self.HowMany}!")
                                self.send_Telegram_msg(f"No {self.BuyBall} on Stock. Try to buy {self.HowMany}!")
                                wait_random_time(self)
                                self.send_privmsg(message.channel, f'!pokeshop {self.BuyBall} {self.HowMany}')


                else:
                    self.MoneyWaitMessage(received_msg)    
            
            else:
                self.Missed = True
                print("Missed the catch on purpose!")  
                self.send_Telegram_msg("Missed the catch on purpose!")


        #Failsave Stuff
    def has_internet_access(self):
        try:
            requests.get("http://www.google.com", timeout=1)
            #print("Check internet")
            return True
        except requests.ConnectionError:
            return False
        
    def loop_for_messages(self):
        last_message_time = time.time()
        internet_was_away = False  # Flag to track if internet was away
        last_internet_check_time = time.time()  # Track last internet access check time
        while True:
            current_time = time.time()  # Get the current time
            # Check for internet access every 10 seconds
            if current_time - last_internet_check_time >= 10:
                if not self.has_internet_access():
                    if not internet_was_away:
                        print("No internet access. Waiting for internet...")
                        self.send_Telegram_msg("No internet access. Waiting for internet...")
                        internet_was_away = True
                    last_internet_check_time = current_time  # Update last check time
                    continue
                else:
                    if internet_was_away:
                        internet_was_away = False
                        print("Internet access restored. Reconnecting to IRC...")
                        self.send_Telegram_msg("Internet access restored. Reconnecting to IRC...")
                        self.connect()  # Reconnect here
                    last_internet_check_time = current_time  # Update last check time



            received_msgs = self.irc.recv(2048).decode()
            if not received_msgs:
                # Handle a situation where the connection is closed unexpectedly
                print("Connection closed unexpectedly. Reconnecting...")
                self.send_Telegram_msg("Connection closed unexpectedly. Reconnecting...")
                self.connect()

            for received_msg in received_msgs.split("\r\n"):
                self.handle_message(received_msg)
                last_message_time = time.time()

            # Check if no message has been received for 18 minutes
            if time.time() - last_message_time > 18 * 60:
                print("No message received for 18 minutes. Reconnecting...")
                self.send_Telegram_msg("No message received for 1 minutes. Reconnecting...") 
                self.connect()

    #Send messages to telegram
    def send_Telegram_msg(self, text):
        token = config.TelegramBotToken
        chat_id = str(config.TelegramChatID)
        #Should not resume if no chat id or token is present
        if not token or not chat_id:
            #print("Token or chat_id is empty.")
            return

        url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" + text 
        results = requests.get(url_req)
        #print(results.json())
            
    def MoneyWaitMessage(self, received_msg): #Just sends emotes if it dosent have money to buy balls.
            Emote = config.Emote
            self.WaitForMoney = True
            message = self.parse_message(received_msg)
            print(
                f"Still not enough money. Need to wait until {self.formatted_time}. Just send emote."
                )
            self.send_Telegram_msg(
                f"Still not enough money. Need to wait until {self.formatted_time}. Just send emote."
                )
            self.Calculatet_Time = datetime.datetime.now() >= self.time_needed
            random_time = random.randint(50, 70)
            if config.ShowRandomeTime:
                print(f"Wait for {random_time} secounds.")
                self.send_Telegram_msg(f"Wait for {random_time} secounds.")
            time.sleep(random_time)
            self.send_privmsg(message.channel, Emote)  
            print(f"Send {Emote} to collect money!") 
            self.send_Telegram_msg(f"Send {Emote} to collect money!")   
        

def main():
    bot = Bot()
    bot.init()
    wait_if_not_in_timeframe(bot, timeframes)

if __name__ == "__main__":
    main()
