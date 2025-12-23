import os
import shutil
import subprocess
import json
import re
from datetime import datetime
import config
import balls


class BotUpdater:
    def __init__(self):
        self.repo_url = "https://github.com/SwissLuckyFox/PokemonCommunityGameBot.git"
        self.backup_dir = "backup_before_update"
        self.temp_dir = "temp_update"
        
        # Configuration keys that should be preserved during update
        self.preserve_keys = [
            "OAUTH_TOKEN",
            "TelegramBotToken",
            "TelegramChatID",
            "DiscordToken",
            "DiscordChannel",
            "DiscordUserID",
            "DiscordUsername",
            "Username",
            "Channels",
            "timeframes",
            # Add other user-specific settings
            "BallToBuy",
            "HowMany",
            "Income",
            "MissPercentage",
            "Pokemonbot",
            "RandomeFrom",
            "RandomeTo",
            "ShowRandomeTime",
            "TimerBallTime",
            "UseRecommended",
            "UseTelegram",
            "AutoBall",
            "AutoCatch",
            "CatchEmote",
            "Emote",
            "CodewordStart",
            "CodewordStop",
            "DiscordDate",
            "DiscordMessage",
            "DiscordMessageDelay",
            "DiscordMessageTime",
            "DiscordAutoTime",
            "BotDiscord",
        ]

    def backup_current_state(self):
        """Create a backup of current configuration and ball data"""
        try:
            # Create backup directory with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.backup_dir}_{timestamp}"
            os.makedirs(backup_path, exist_ok=True)
            
            # Backup config.py
            if os.path.exists("config.py"):
                shutil.copy2("config.py", os.path.join(backup_path, "config.py"))
            
            # Backup balls.py
            if os.path.exists("balls.py"):
                shutil.copy2("balls.py", os.path.join(backup_path, "balls.py"))
            
            print(f"Backup created at: {backup_path}")
            return backup_path, True
        except Exception as e:
            print(f"Backup failed: {e}")
            return None, False

    def extract_current_config(self):
        """Extract current configuration values that should be preserved"""
        preserved_config = {}
        
        for key in self.preserve_keys:
            if hasattr(config, key):
                preserved_config[key] = getattr(config, key)
        
        return preserved_config

    def extract_current_balls(self):
        """Extract current ball stock data"""
        return {ball["Name"]: ball["Stock"] for ball in balls.LIST}

    def pull_latest_version(self):
        """Pull the latest version from GitHub"""
        try:
            # Check if git is available
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    return False, "Git is not installed or not available in PATH"
            except FileNotFoundError:
                return False, "Git is not installed. Please install Git from https://git-scm.com/"
            except Exception as e:
                return False, f"Cannot access Git: {str(e)}"
            
            # Check if we're in a git repository
            result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # We're in a git repo, pull updates
                print("Pulling latest changes from GitHub...")
                result = subprocess.run(["git", "pull", "origin", "master"], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print("Successfully pulled latest version")
                    return True, "Update successful"
                else:
                    return False, f"Git pull failed: {result.stderr}"
            else:
                # Not a git repo, try to clone to temp directory
                print("Not a git repository. Downloading latest version...")
                
                # Remove temp directory if it exists
                if os.path.exists(self.temp_dir):
                    shutil.rmtree(self.temp_dir)
                
                # Clone repository to temp directory
                result = subprocess.run(
                    ["git", "clone", self.repo_url, self.temp_dir],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return False, f"Git clone failed: {result.stderr}"
                
                return True, "Downloaded latest version to temp directory"
                
        except Exception as e:
            return False, f"Update failed: {str(e)}"

    def merge_config(self, preserved_config):
        """Merge preserved configuration with new config file"""
        try:
            # Read the new config file
            with open("config.py", "r", encoding="utf-8") as f:
                config_content = f.read()
            
            # Update each preserved key in the new config
            for key, value in preserved_config.items():
                # Create regex pattern to find the key
                pattern = rf'^{re.escape(key)}\s*=\s*.*$'
                
                # Format the value properly
                if isinstance(value, str):
                    formatted_value = f'"{value}"'
                elif isinstance(value, bool):
                    formatted_value = str(value)
                elif isinstance(value, dict):
                    formatted_value = json.dumps(value, indent=4)
                elif isinstance(value, list):
                    formatted_value = json.dumps(value)
                else:
                    formatted_value = str(value)
                
                # Replace the line
                replacement = f'{key} = {formatted_value}'
                config_content = re.sub(pattern, replacement, config_content, flags=re.MULTILINE)
            
            # Write the updated config
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
            
            print("Configuration merged successfully")
            return True
        except Exception as e:
            print(f"Config merge failed: {e}")
            return False

    def merge_balls(self, preserved_balls):
        """Merge preserved ball stock with new ball list"""
        try:
            # Reload balls module to get the new structure
            import importlib
            importlib.reload(balls)
            
            # Update stock for existing balls
            for ball in balls.LIST:
                if ball["Name"] in preserved_balls:
                    ball["Stock"] = preserved_balls[ball["Name"]]
            
            # Save the updated ball list
            with open("balls.py", "w", encoding="utf-8") as f:
                f.write("LIST = [\n")
                for ball in balls.LIST:
                    f.write(f'    {{"Name": "{ball["Name"]}", "Stock": {ball["Stock"]}}},\n')
                f.write("]\n")
            
            print("Ball stock merged successfully")
            return True
        except Exception as e:
            print(f"Ball merge failed: {e}")
            return False

    def update_bot(self):
        """Main update function"""
        log = []
        
        # Step 1: Backup current state
        log.append("Step 1: Creating backup...")
        backup_path, success = self.backup_current_state()
        if not success:
            log.append("❌ Backup failed! Aborting update.")
            return False, "\n".join(log)
        log.append(f"✓ Backup created at: {backup_path}")
        
        # Step 2: Extract current configuration
        log.append("\nStep 2: Extracting current configuration...")
        preserved_config = self.extract_current_config()
        preserved_balls = self.extract_current_balls()
        log.append(f"✓ Preserved {len(preserved_config)} config values")
        log.append(f"✓ Preserved ball stock data")
        
        # Step 3: Pull latest version
        log.append("\nStep 3: Downloading latest version from GitHub...")
        success, message = self.pull_latest_version()
        if not success:
            log.append(f"❌ {message}")
            log.append(f"\nUpdate failed. Your backup is at: {backup_path}")
            return False, "\n".join(log)
        log.append(f"✓ {message}")
        
        # Step 4: Merge configuration
        log.append("\nStep 4: Merging configuration...")
        if self.merge_config(preserved_config):
            log.append("✓ Configuration merged successfully")
        else:
            log.append("⚠ Configuration merge had issues")
        
        # Step 5: Merge ball stock
        log.append("\nStep 5: Merging ball stock...")
        if self.merge_balls(preserved_balls):
            log.append("✓ Ball stock merged successfully")
        else:
            log.append("⚠ Ball stock merge had issues")
        
        # Step 6: Cleanup
        if os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                log.append("\nStep 6: Cleaned up temporary files")
            except:
                pass
        
        log.append("\n✅ Update completed successfully!")
        log.append(f"Backup location: {backup_path}")
        log.append("\n⚠ IMPORTANT: Please restart the bot for changes to take effect!")
        
        return True, "\n".join(log)

    def check_for_updates(self):
        """Check if updates are available on GitHub"""
        try:
            # Check if git is available
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=5)
                if result.returncode != 0:
                    return None, "Git is not installed. Please install Git from https://git-scm.com/ to use the update feature."
            except FileNotFoundError:
                return None, "Git is not installed or not in PATH. Please install Git from https://git-scm.com/ and ensure it's added to your system PATH."
            except Exception as e:
                return None, f"Cannot access Git: {str(e)}. Please install Git from https://git-scm.com/"
            
            # Check if we're in a git repository
            result = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                # Fetch latest changes
                subprocess.run(["git", "fetch", "origin", "master"], capture_output=True, text=True, timeout=30)
                
                # Check if local is behind remote
                result = subprocess.run(
                    ["git", "rev-list", "HEAD..origin/master", "--count"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    commits_behind = int(result.stdout.strip())
                    if commits_behind > 0:
                        return True, f"Updates available ({commits_behind} new commits)"
                    else:
                        return False, "You are on the latest version"
                else:
                    return None, "Could not check for updates"
            else:
                return None, "Not a git repository. Cannot check for updates automatically."
                
        except FileNotFoundError:
            return None, "Git is not installed or not in PATH. Please install Git from https://git-scm.com/ and ensure it's added to your system PATH."
        except Exception as e:
            return None, f"Error checking for updates: {str(e)}"


if __name__ == "__main__":
    updater = BotUpdater()
    
    # Check for updates
    print("Checking for updates...")
    has_updates, message = updater.check_for_updates()
    print(message)
    
    if has_updates:
        response = input("\nDo you want to update now? (yes/no): ")
        if response.lower() in ["yes", "y"]:
            success, log = updater.update_bot()
            print("\n" + log)
