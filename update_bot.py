#!/usr/bin/env python
"""
Standalone update script for PokemonCommunityGameBot
This script can be run directly to update the bot from GitHub
"""

from updater import BotUpdater
import sys


def main():
    print("=" * 60)
    print("PokemonCommunityGameBot Updater")
    print("=" * 60)
    
    updater = BotUpdater()
    
    # Check for updates
    print("\nChecking for updates...")
    has_updates, message = updater.check_for_updates()
    print(message)
    
    if has_updates is None:
        print("\n⚠ Could not check for updates automatically.")
        print("You can still try to update, but it might not work.")
        response = input("\nDo you want to try updating anyway? (yes/no): ")
    elif has_updates is False:
        print("\nYou are already on the latest version!")
        response = input("\nDo you want to force an update anyway? (yes/no): ")
    else:
        print("\n✓ Updates are available!")
        response = input("\nDo you want to update now? (yes/no): ")
    
    if response.lower() not in ["yes", "y"]:
        print("\nUpdate cancelled.")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("Starting Update Process")
    print("=" * 60)
    print("\nIMPORTANT: Your configuration (tokens, settings) and ball stock")
    print("will be automatically preserved during the update.")
    print("\n")
    
    # Run the update
    success, log = updater.update_bot()
    
    print("\n" + "=" * 60)
    print("Update Log")
    print("=" * 60)
    print(log)
    print("\n" + "=" * 60)
    
    if success:
        print("\n✅ Update completed successfully!")
        print("\n⚠ IMPORTANT: Please restart all bot processes for changes to take effect!")
        print("\nYou may need to:")
        print("  1. Stop all running bot processes")
        print("  2. Run: pip install -r requirements.txt (if dependencies changed)")
        print("  3. Restart the bots")
    else:
        print("\n❌ Update failed!")
        print("Your backup is available if you need to restore.")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
