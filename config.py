import datetime
#Your Oauth token
OAUTH_TOKEN = "oauth:4qxehhdsg7w1o9kisiawdc0aw6551y"
#Your Username.
Username = "LuckyFox__"
#What Channels to join.
Channels = ['deemonrider',]
#User The bot should Listen to.
Pokemonbot = 'pokemoncommunitygame'
#Auto Catcher switch (True/Fals)
AutoCatch = True
#use Pokeballs if no ball is spesified (True/False)
AutoBall = True
#What and How many Balls should be bought. Make i recommend Pokeballs. But you do you.
BallToBuy = 'Pokeball'
HowMany = 10
#Codeword to Resume. Make shure the bot dosent type it itself! Dont use deemon emotes.
CodewordStop = 'Banana'
CodewordStart = 'Bananas'
#Message or Emote it sends to Collect Coins
Emote = 'deemon8Hype'
#Command or Emote to use to throw balls
CatchEmote = 'deemon8Catch'

#Timeframes where the Bot sould run. With a sprinkle of randome time =)
timeframes = {
    "Monday": {
        "start": "06:00",
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
        "start": "07:30",
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