#Your Oauth token
OAUTH_TOKEN = ""
#Your Username.
Username = ""
#What Channels to join.
Channels = ['',]
#User The bot should Listen to.
Pokemonbot = ''
#Telegram Bot Token
TelegramBotToken = ""
TelegramChatID = 123456789
#IRC Server Connection
irc_server = 'irc.chat.twitch.tv'
irc_port = 6697
#Auto Catcher switch (True/Fals)
AutoCatch = True
#use Pokeballs if no ball is spesified (True/False)
AutoBall = True
#What and How many Balls should be bought. Make i recommend Pokeballs. But you do you.
BallToBuy = 'Pokeball'
HowMany = 10
#Codeword to Resume. Make shure the bot dosent type it itself! Dont use deemon emotes.
CodewordStop = 'Banana'
CodewordStart = 'Apple'
#Message or Emote it sends to Collect Coins
Emote = 'deemon8Hype'
#Command or Emote to use to throw balls
CatchEmote = 'deemon8Catch'
#Your money income per Houer
Income = 800
#The timeframe used to randomise the throws (in secounds)
RandomeFrom = 5
RandomeTo = 10
#Shows randome time in Messages True/False
ShowRandomeTime = True
#Timeframes where the Bot sould run. With a sprinkle of randome time =)
timeframes = {
    "Monday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    },
    "Tuesday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    },
    "Wednesday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    },
    "Thursday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    },
    "Friday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    },
    "Saturday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    },
    "Sunday": {
        "start": "07:00",
        "end": "23:30",
        "random_interval": {
            "min": 15,
            "max": 30
        }
    }
}
