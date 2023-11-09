#!/usr/bin/env python
import socket
import ssl
import datetime
import random
import json
import time
from turtle import home
import pokemon
import balls
from collections import namedtuple
from config import timeframes
import config
AutoCatch = config.AutoCatch

#Watch if its time to Start with a randome leeway.
def wait_if_not_in_timeframe(timeframes):
    # Get current day and time
    now = datetime.datetime.now()
    current_day = now.strftime("%A")
    current_time = now.strftime("%H:%M")

    # Get start and end time for current day
    start_time = timeframes[current_day]["start"]
    end_time = timeframes[current_day]["end"]

    # If current time is not in the timeframe, wait
    if not(start_time <= current_time <= end_time):
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

        print(f"Still Seeping for {wait_time/60} minutes. Will start again at {(now + datetime.timedelta(seconds=wait_time)).strftime('%H:%M')}.")

        # Sleep for the calculated time
        time.sleep(wait_time)


Message = namedtuple(
    'Message',
    'prefix user channel irc_command irc_args text text_command text_args',
)


def remove_prefix(string, prefix):
    if not string.startswith(prefix):
        return string
    return string[len(prefix):]

    #Randome Time
def wait_random_time():
    # Generate a random number in secounds
    random_time = random.randint(5, 10)
    time.sleep(random_time)
     
class Bot:
    wait_if_not_in_timeframe(timeframes)
    def __init__(self):
        self.irc_server = 'irc.chat.twitch.tv'
        self.irc_port = 6697
        self.oauth_token = config.OAUTH_TOKEN
        self.username = config.Username
        self.channels = config.Channels
        self.PokeBot = config.Pokemonbot.lower()
        self.command_prefix = '@'

    def init(self):
        self.connect()

    def send_privmsg(self, channel, text):
        self.send_command(f'PRIVMSG #{channel} :{text}')

    def send_command(self, command):
        self.irc.send((command + '\r\n').encode())
        #if 'PASS' not in command:
            #print(f'< {command}')
        
        
    def connect(self):
        self.irc = ssl.wrap_socket(socket.socket())
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command(f'PASS {self.oauth_token}')
        self.send_command(f'NICK {self.username}')
        for channel in self.channels:
            self.send_command(f'JOIN #{channel}')
            print (f'Go to {channel}`s Safarizone with {self.username}. Lets Catch some Pokemon!')
        self.loop_for_messages()
        

    def get_user_from_prefix(self, prefix):
        domain = prefix.split('!')[0]
        if domain.endswith('.tmi.twitch.tv'):
            return domain.replace('.tmi.twitch.tv', '')
        if 'tmi.twitch.tv' not in domain:
            return domain
        return None
    
    #Splitting Message into parts to Filter it more easely
    def parse_message(self, received_msg):
        parts = received_msg.split(' ')

        prefix = None
        user = None
        channel = None
        text = None
        text_command = None
        text_args = None
        irc_command = None
        irc_args = None

        if parts[0].startswith(':'):
            prefix = remove_prefix(parts[0], ':')
            user = self.get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(':')),
            None
        )
        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = ' '.join(text_parts)
            if text_parts[0].startswith(self.command_prefix):
                text_command = remove_prefix(text_parts[0], self.command_prefix)
                text_args = text_parts[1:]
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]

        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith('#')),
            None
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
  
         
    def handle_message(self, received_msg):
        wait_if_not_in_timeframe(timeframes)
        if len(received_msg) == 0:
            return
        master = config.Pokemonbot.lower()
        message = self.parse_message(received_msg)
        trainer = self.username
        BuyBall = config.BallToBuy
        UserLow = config.Username.lower()
        Emote = config.Emote
        AutoCatch = config.AutoCatch
        CatchEmote = config.CatchEmote
        #if message.user == master:
           # print(f'> {message}')
        # Filter Messanges and throws Balls according to pokemon.py file
        if message.user == master and message.text is not None:
            if 'Catch it using !pokecatch' in message.text: 
                if config.AutoCatch:
                    for word in pokemon.LIST:
                        word_parts = word.split(':')
                        if word_parts[0] in message.text:
                            print(f"Its a {word_parts[0]}!")
                            #Compare Thrown Balls to list an Print
                            if word_parts[1] == 'True':
                                if word_parts[2] not in balls.BALLS:
                                    if config.AutoBall:
                                        word_parts[2] = 'Pokeball'
                                        wait_random_time()
                                        self.send_privmsg(message.channel, CatchEmote)
                                        print(f'Throw {word_parts[2]}!')
                                        Ball = word_parts[2]
                                        break
                                else: #Timerball and Quickball logic
                                    if word_parts[2] in balls.BALLS:
                                        if word_parts[2] == 'Quickball':
                                            print('''You don't know how fast i really am! Quickball!''')
                                            self.send_privmsg(message.channel, f'{CatchEmote} {word_parts[2]}')
                                        elif word_parts[2] == 'Timerball':
                                            print('Its a Timerball. Slowpoke time!')
                                            time.sleep(75)
                                            self.send_privmsg(message.channel, f'{CatchEmote} {word_parts[2]}')
                                        else:
                                            wait_random_time()
                                            self.send_privmsg(message.channel, f'{CatchEmote} {word_parts[2]}')
                                            print(f'Throw {word_parts[2]}!')
                                            if word_parts[2] != 'Greatball' or 'Pokeball' or 'Ultraball':
                                               None
                                            else:   
                                                Ball = word_parts[2]
                                                break
                            else:#Sends emote if Pokemon sould not be catched.
                                print (f'A {word_parts[0]}... Ill Pass on that! Send Emote!')
                                wait_random_time()
                                self.send_privmsg(message.channel, Emote)
                else: #Just sends emotes if Autocatch is off.
                    print('Autocatch is off. Do we have Balls to throw? If yes Type the Codeword in chat to resume.')
                    wait_random_time()
                    self.send_privmsg(message.channel, Emote)
                 
            #Try to buy balls  
            elif f'@{UserLow} ''''You don't own that ball. Check the extension to see your items''' == message.text:     
                wait_random_time()
                self.send_privmsg(message.channel, f'!pokeshop {BuyBall} {HowMany}')
                print(f'Try to buy {BuyBall}!')
            
            #Try to throw after Purchase   
            elif f'@{UserLow} ''Purchase successful!' == message.text:
                if BuyBall != 'Pokeball':
                    wait_random_time()
                    self.send_privmsg(message.channel, f'{CatchEmote} {BuyBall}')
                elif BuyBall == 'Pokeball':
                    wait_random_time()
                    self.send_privmsg(message.channel, CatchEmote)
                          
            #Look for failed purachase               
            elif 'You cant buy that item.' in message.text:
                if f'@{UserLow}' in message.text:
                    print(f'Could not buy {BuyBall}s! Dont catch anymore!')
                    config.AutoCatch = False
                    
            #Check if catched       
            elif 'has been caught by' in message.text:
                if AutoCatch:
                    if UserLow in message.text:
                        print('Catched it! =D')
                    else:
                        print('No luck =(')
            elif 'No one caught it.' in message.text:
                if AutoCatch:
                    print('No luck =(')
                

        #Ping Pong with Twitch
        if message.irc_command == 'PING':
            self.send_command('PONG :tmi.twitch.tv')
            #print('Ping Pong Twitch')

 
        #Resume Autocatch with Codeword
        if message.user == UserLow and message.text is not None:
            if config.CodewordStart in message.text:
                config.AutoCatch = True
                print('Resume Autocatch')
            if config.CodewordStop in message.text:
                config.AutoCatch = False
    
                        
    
    def loop_for_messages(self):
        while True:
            received_msgs = self.irc.recv(2048).decode()
            for received_msg in received_msgs.split('\r\n'):
                self.handle_message(received_msg)
            
        
def main():
    bot = Bot()
    bot.init()
    
if __name__ == '__main__':
    main()
