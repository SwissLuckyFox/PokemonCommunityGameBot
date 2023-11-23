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
from simpletelegrambot import telegrambot
import requests

def on_message_receive(bot, message):

    utc_time = datetime.utcnow()
    msg_time = utc_time.strftime('%Y-%m-%d %H:%M:%S (UTC)')
    msg_text = message['text']
    bot.send_message('Pong')
    print(msg_time, msg_text)

    # Watch if its time to Start with a randome leeway.      
def wait_if_not_in_timeframe(self, timeframes):
    # Get current day and time
    now = datetime.datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    # Get start and end time for current day
    start_time = timeframes[current_day]["start"]
    end_time = timeframes[current_day]["end"]

    # If current time is not in the timeframe, wait
    if not (start_time <= current_time <= end_time):
        # Calculate time difference in seconds
        start_time_obj = datetime.datetime.strptime(start_time, "%H:%M")
        current_time_obj = datetime.datetime.strptime(current_time, "%H:%M")
        time_diff = (start_time_obj - current_time_obj).seconds

        # Generate a random interval within the given min and max
        random_interval_min = timeframes[current_day]["random_interval"]["min"]
        random_interval_max = timeframes[current_day]["random_interval"]["max"]
        random_interval = (
            random.randint(random_interval_min, random_interval_max) * 60
        )  # convert to seconds

        # Add the random interval to the time difference
        wait_time = time_diff + random_interval
        wait_time_Format = wait_time // 60
        wait_date = (now + datetime.timedelta(seconds=wait_time)).strftime('%H:%M')
        print(
            f"Still Seeping for {wait_time_Format} minutes. Will start again at {wait_date}."
            )
        self.send_Telegram_msg(
            f"Still Seeping for {wait_time_Format} minutes. Will start again at {wait_date}."
            )
        time.sleep(wait_time)
        print(f"Ring! Riing! Sleeptime is over!")
        self.send_Telegram_msg(f"Ring! Riing! Sleeptime is over!")
        bot.connect()
        
        return False
        # Sleep for the calculated time
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
    random_time = random.randint(config.RandomeFrom, config.RandomeTo)
    print(f"Wait for {random_time} secounds.")
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

    def init(self):
        self.connect()

    def send_privmsg(self, channel, text):
        self.send_command(f"PRIVMSG #{channel} :{text}")

    def send_command(self, command):
        self.irc.send((command + "\r\n").encode())
        # if 'PASS' not in command:
        # print(f'< {command}')

    def connect(self):
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
    
        #Calculate the time it needs to get the desired balance
    def CalculateTimeNeed(self, NeededMoney, Balance, Income,):
        hours_needed = (NeededMoney - Balance) / Income
        self.time_needed = datetime.datetime.now() + datetime.timedelta(hours=hours_needed)
        self.Calculatet_Time = datetime.datetime.now() >= self.time_needed
        self.formatted_time = self.time_needed.strftime('%H:%M')
        print(
            f'I have {Balance}$. I need {NeededMoney}$ My income is {Income}$'
            )
        print(
            f'Will not catch until {self.formatted_time}. Need Money to buy Balls'
            )
        self.send_Telegram_msg(
            f'I have {Balance}$. I need {NeededMoney}$ My income is {Income}$'
            )
        self.send_Telegram_msg(
            f'Will not catch until {self.formatted_time}. Need Money to buy Balls'
            )
        return self.time_needed, self.Calculatet_Time, self.formatted_time

    def handle_message(self, received_msg):
        wait_if_not_in_timeframe(self, timeframes)
        if len(received_msg) == 0:
            return
        if not hasattr(self, 'Calculatet_Time'):
            self.Calculatet_Time = True
        master = config.Pokemonbot.lower()
        message = self.parse_message(received_msg)
        trainer = self.username
        BuyBall = config.BallToBuy
        HowMany = config.HowMany
        UserLow = config.Username.lower()
        Emote = config.Emote
        CatchEmote = config.CatchEmote
        #if message.user == master:
            #if wait_if_not_in_timeframe(self, timeframes):
                #print(f'> {message}')
        # Filter Messanges and throws Balls according to pokemon.py file
        if message.user == master and message.text is not None:
            if wait_if_not_in_timeframe(self, timeframes):
                if 'Catch it using !pokecatch' in message.text: 
                    if AutoCatch:
                        if self.Calculatet_Time:
                            for word in pokemon.LIST:
                                word_parts = word.split(':')
                                if word_parts[0] in message.text:
                                    print(f"Its a {word_parts[0]}!")
                                    self.send_Telegram_msg(f"Its a {word_parts[0]}!")
                                    #Compare Thrown Balls to list an Print
                                    if word_parts[1] == 'True':
                                        if word_parts[2] not in balls.BALLS:
                                            if config.AutoBall:
                                                word_parts[2] = 'Pokeball'
                                                wait_random_time(self)
                                                self.send_privmsg(message.channel, CatchEmote)
                                                print(f'Throw {word_parts[2]}!')
                                                self.send_Telegram_msg(f'Throw {word_parts[2]}!')
                                                Ball = word_parts[2]
                                            else:
                                                print(
                                                    'No Ball was defined in the Config and Autoball is off. Just send a Emote to collect money.'
                                                    )
                                                self.send_Telegram_msg(
                                                    'No Ball was defined in the Config and Autoball is off. Just send a Emote to collect money.'
                                                    )
                                                self.send_privmsg(message.channel, Emote)
                                        else: #Timerball and Quickball logic
                                            if word_parts[2] in balls.BALLS:
                                                if word_parts[2] == 'Quickball':
                                                    print("Quickball! Throw Fast!")
                                                    self.send_Telegram_msg("Quickball! Throw Fast!")
                                                    self.send_privmsg(message.channel, f'{CatchEmote} {word_parts[2]}')
                                                elif word_parts[2] == 'Timerball':
                                                    print('Its a Timerball. Slowpoke time!')
                                                    self.send_Telegram_msg('Its a Timerball. Slowpoke time!')
                                                    time.sleep(80)
                                                    self.send_privmsg(message.channel, f'{CatchEmote} {word_parts[2]}')
                                                else:
                                                    wait_random_time(self)
                                                    self.send_privmsg(message.channel, f'{CatchEmote} {word_parts[2]}')
                                                    print(f'Throw {word_parts[2]}!')
                                    else:#Sends emote if Pokemon sould not be catched.
                                        print (f'A {word_parts[0]}... Ill Pass on that! Send Emote!')
                                        self.send_Telegram_msg(f'A {word_parts[0]}... Ill Pass on that! Send Emote!')
                                        random_time = random.randint(50, 70)
                                        time.sleep(random_time)
                                        self.send_privmsg(message.channel, Emote)
                                        print(f"Send {Emote} to collect money!") 
                                        self.send_Telegram_msg(f"Send {Emote} to collect money!")
                        else:   #Just sends emotes if it dosent have money to buy balls
                            print(
                                f'Still not enough money. Need to wait until {self.formatted_time}. Just send emote.'
                                )
                            self.send_Telegram_msg(
                                f'Still not enough money. Need to wait until {self.formatted_time}. Just send emote.'
                                )
                            self.Calculatet_Time = datetime.datetime.now() >= self.time_needed
                            random_time = random.randint(50, 70) 
                            wait_random_time(self)
                            self.send_privmsg(message.channel, Emote)  
                            print(f"Send {Emote} to collect money!") 
                            self.send_Telegram_msg(f"Send {Emote} to collect money!")              
                    else:   #Just sends emotes if Autocatch is off.
                            print(
                                'Autocatch is off. Do we have Balls to throw? If yes Type the Codeword in chat to resume.'
                                ) 
                            self.send_Telegram_msg(
                                'Autocatch is off. Do we have Balls to throw? If yes Type the Codeword in chat to resume.'
                                ) 
                            random_time = random.randint(50, 70) 
                            wait_random_time(self)
                            self.send_privmsg(message.channel, Emote) 
                            print(f"Send {Emote} to collect money!")  
                            self.send_Telegram_msg(f"Send {Emote} to collect money!")   
                 
                #Try to buy balls  
                elif '''You don't own that ball. Check the extension to see your items''' in message.text:
                    if f'@{UserLow}' in message.text:
                        wait_random_time(self)
                        self.send_privmsg(message.channel, f'!pokeshop {BuyBall} {HowMany}')
                        print(f"""I dont have {BuyBall}'s!""")
                        self.send_Telegram_msg(f"""I dont have {BuyBall}'s!""")
                        print(f'Try to buy {BuyBall}!')
                        self.send_Telegram_msg(f'Try to buy {BuyBall}!')
                
                #Try to throw after Purchase   
                elif f'@{UserLow} ''Purchase successful!' == message.text:
                    if BuyBall != 'Pokeball':
                        print(f'Bought {HowMany} {BuyBall}s!')
                        self.send_Telegram_msg(f'Bought {HowMany} {BuyBall}s!')
                        wait_random_time(self)
                        self.send_privmsg(message.channel, f'{CatchEmote} {BuyBall}')
                        print(f'Throw {BuyBall}!')
                        self.send_Telegram_msg(f'Throw {BuyBall}!')
                    elif BuyBall == 'Pokeball':
                        print(f'Bought {HowMany} {BuyBall}s!')
                        self.send_Telegram_msg(f'Bought {HowMany} {BuyBall}s!')
                        wait_random_time(self)
                        self.send_privmsg(message.channel, CatchEmote)
                        print(f'Throw {BuyBall}!')
                        self.send_Telegram_msg(f'Throw {BuyBall}!')
                            
                #Look for failed purachase               
                elif '''You don't have enough''' in message.text:
                    if f'@{UserLow}' in message.text:
                        match = re.search(r'\D*(\d+)', message.text)
                        if match:
                            self.NeededMoney = int(match.group(1))
                            print(f'You need {int(match.group(1))} Pokedollers!')
                            wait_random_time(self)
                            self.send_privmsg(message.channel, '!pokepass')
                            print('Get Balance')
                            self.send_Telegram_msg("It broke out! =(")
                #Check if catched       
                elif 'has been caught by:' in message.text:
                    if AutoCatch == True:
                        if self.Calculatet_Time:
                            if UserLow in message.text:
                                print('Catched it! =D')
                                self.send_Telegram_msg("Catched it! =D")
                            else:
                                print('It broke out! =(')
                                self.send_Telegram_msg("It broke out! =(")
                elif 'No one caught it.' in message.text:
                    if AutoCatch == True:
                        if self.Calculatet_Time:
                            print('It broke out! =(')
                            self.send_Telegram_msg("It broke out! =(")
                
                #Gets the Balance and starts Calculation
                elif 'Balance' in message.text:
                    if UserLow in message.text:
                        match = re.search(r'\$(\d+)', message.text)
                        if match:
                            self.Income = config.Income 
                            self.Balance = int(match.group(1))
                            #print(f'Your balance is {int(match.group(1))}')
                            self.CalculateTimeNeed(self.NeededMoney, self.Balance, self.Income)               
        # Ping Pong with Twitch
        if message.irc_command == "PING":
            self.send_command("PONG :tmi.twitch.tv")
            # print('Ping Pong Twitch')

        #Resume Autocatch with Codeword
        if message.user == UserLow and message.text is not None:
            if config.CodewordStart in message.text:
                self.AutoCatch = True
                print('Resume Autocatch')
                self.send_Telegram_msg("Resume Autocatch")
            if config.CodewordStop in message.text:
                self.AutoCatch = False
                print('Stop Autocatch')
                self.send_Telegram_msg("Stop Autocatch")
                     
    def loop_for_messages(self):
        while True:
            received_msgs = self.irc.recv(2048).decode()
            for received_msg in received_msgs.split("\r\n"):
                self.handle_message(received_msg)

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

        

def main():
    bot = Bot()
    bot.init()
    wait_if_not_in_timeframe(bot, timeframes)

if __name__ == "__main__":
    main()
