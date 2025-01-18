import subprocess
import os
import sys

# Importiere die Konfigurationsdatei
try:
    from config import BotDiscord, UseTelegram
except ImportError:
    print("Die config.py Datei fehlt oder ist fehlerhaft.")
    sys.exit(1)

# Funktionen zum Starten der Bots
def start_script(script_name):
    try:
        subprocess.Popen([sys.executable, script_name])
        print(f"{script_name} wurde gestartet.")
    except Exception as e:
        print(f"Fehler beim Starten von {script_name}: {e}")

if __name__ == "__main__":
    # Starte die Bots basierend auf der Konfiguration
    if BotDiscord:
        start_script("Discord_Bot.py")
    else:
        print("Discord Bot ist deaktiviert.")

    if UseTelegram:
        start_script("Telegram_Bot.py")
    else:
        print("Telegram Bot ist deaktiviert.")

    # PCG_Bot.py wird unabhängig gestartet
    start_script("PCG_Bot.py")
