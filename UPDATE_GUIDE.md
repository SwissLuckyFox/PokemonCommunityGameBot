# Bot Update System

This bot now includes an automatic update system that can pull the latest version from GitHub while preserving your configuration and data.

## Features

- ✅ Automatic updates from GitHub
- ✅ Preserves all your tokens and credentials (Discord, Telegram, Twitch)
- ✅ Preserves your ball stock data
- ✅ Preserves all your custom settings
- ✅ Creates automatic backups before updating
- ✅ Can be triggered via Telegram commands or run standalone

## Prerequisites

- Git must be installed on your system
- The bot files should be in a git repository (cloned from GitHub)

## How to Use

### Method 1: Via Telegram Bot

1. Send `!CheckUpdate` to check if updates are available
2. If updates are available, send `!Update` to install them
3. Restart the bot manually after the update completes

### Method 2: Standalone Script

Run the update script directly:

```bash
python update_bot.py
```

Follow the on-screen prompts to complete the update.

### Method 3: Using the updater module

You can also use the updater in your own scripts:

```python
from updater import BotUpdater

updater = BotUpdater()

# Check for updates
has_updates, message = updater.check_for_updates()
print(message)

# Perform update
if has_updates:
    success, log = updater.update_bot()
    print(log)
```

## What Gets Preserved

The following configuration values are automatically preserved during updates:

### Credentials & Tokens
- `OAUTH_TOKEN` - Twitch OAuth token
- `TelegramBotToken` - Telegram bot token
- `TelegramChatID` - Telegram chat ID
- `DiscordToken` - Discord token
- `DiscordUserID` - Discord user ID
- `Username` - Twitch username

### Bot Settings
- `Channels` - Twitch channels to monitor
- `BallToBuy` - Default ball to purchase
- `HowMany` - Number of balls to buy
- `Income` - Income per catch
- `MissPercentage` - Intentional miss percentage
- `Pokemonbot` - Pokemon bot username
- `UseRecommended` - Use recommended balls
- `AutoBall` - Auto ball mode
- `AutoCatch` - Auto catch mode
- `timeframes` - Active time schedules

### Ball Stock
- All ball stock quantities are preserved

## Backup System

Before each update, the system automatically creates a timestamped backup:

- Location: `backup_before_update_YYYYMMDD_HHMMSS/`
- Contains: `config.py` and `balls.py`

If something goes wrong, you can manually restore from the backup:

```bash
# Copy the backup files back
copy backup_before_update_YYYYMMDD_HHMMSS\config.py config.py
copy backup_before_update_YYYYMMDD_HHMMSS\balls.py balls.py
```

## Troubleshooting

### "Git is not installed or not available in PATH"

Install Git from https://git-scm.com/ and make sure it's in your system PATH.

### "Not a git repository"

If you downloaded the files as a ZIP instead of cloning:

```bash
# Initialize git and link to the repository
git init
git remote add origin https://github.com/SwissLuckyFox/PokemonCommunityGameBot.git
git fetch
git reset --hard origin/master
```

### Update fails mid-process

Your backup is located in `backup_before_update_YYYYMMDD_HHMMSS/`. You can restore your files from there.

### Configuration not preserved

Check the `preserve_keys` list in `updater.py`. You can add additional keys that should be preserved during updates.

## After Updating

1. **Stop all bot processes** (Discord, Telegram, Twitch bots)
2. **Check if requirements changed**: `pip install -r requirements.txt`
3. **Restart all bots**

## Telegram Commands

- `!CheckUpdate` - Check if updates are available
- `!Update` - Download and install the latest version
- `!Commands` - Show all available commands

## Advanced: Customizing Preserved Keys

Edit `updater.py` and modify the `preserve_keys` list in the `BotUpdater` class:

```python
self.preserve_keys = [
    "OAUTH_TOKEN",
    "TelegramBotToken",
    # Add your custom keys here
    "MyCustomSetting",
]
```

## Security Note

Your tokens and credentials are only stored locally. The update system reads them from your current `config.py`, updates the code, and writes them back to the new `config.py`. Nothing is sent to GitHub or any external service.
