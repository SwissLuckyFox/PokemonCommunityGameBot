# PokemonCommunityGameBot
A Small Bot for Twitch PCG Chat game.

Its my first dip into programming. I use it to learn it a little becouse i need somting useful to be motivaded.

The bot manages fundamental chat tasks and is capable of functioning 24/7. 
To set it up, simply provide your OAuth token and username. With these details, the bot is ready to go. 
While you have the option to change the channel, using the default channel is recommended as it is consistently online.


Features:


Timeframes:

  Configure specific timeframes for the bot's activity. 
  Outside these periods, the bot remains inactive. 
  Each day can have distinct settings, and a random element is introduced to prevent dedection.


Autocatch:

  It automaticly sends the preferred message to catch. It can be chanced in the config.
  Reads the spawned pokemon and compares it to the pokemon table to see if it should be catched or not. 
  It checks the pokemon file and uses the configeret Ball. If no ball is set, it uses Pokeballs. This can be turned off.
  Respects Timer and Fastballs and throws them accordingly.
  Also adds a randome time to it just to not throw it exactly the same every time.


Auto Purchase:

  Automatically acquires Pokeballs when the inventory is depleted. Ensure the ball is available in the shop.

  
Balance and Time Needed Calculation:

  If there's insufficient funds, the bot calculates the time required to reach the desired balance based on average income.
  
