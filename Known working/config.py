import datetime
#Your Oauth token
OAUTH_TOKEN = "oauth:4qxehhdsg7w1o9kisiawdc0aw6551y"
#Your Username
Username = "LuckyFox__"
#What Channels to join.
Channels = ['DeemonRider',]
#User The bot should Listen to.
Pokemonbot = 'PokemonCommunityGame'
#Auto Catcher switch (Yes/No)
AutoCatch = True
#use Pokeballs if no ball is spesified (Yes/No)
AutoBall = True
#What Ball should be bought. Make i recommend Pokeballs. But you do you.
BallToBuy = 'Pokeball'
#Codeword to Resume. Make shure the bot dosent type it itself! Dont use deemon emotes.
Codeword = 'Banana'

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