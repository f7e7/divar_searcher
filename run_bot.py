#!/usr/bin/env python3
"""
Simple script to run the Divar Search Telegram Bot
"""

import sys
import os

def main():
    """Run the bot with error checking"""
    print("🚀 Starting Divar Search Telegram Bot...")

    # Check required packages with correct import names
    required_packages = [
        ('telegram', 'python-telegram-bot'),
        ('requests', 'requests'),
        ('bs4', 'beautifulsoup4'),
        ('openpyxl', 'openpyxl'),
        ('selenium', 'selenium')
    ]
    missing_packages = []

    for import_name, display_name in required_packages:
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(display_name)

    if missing_packages:
        print(f"❌ ERROR: Missing required packages: {', '.join(missing_packages)}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

    # Check if config.py exists and has token
    try:
        import config
        if config.BOT_TOKEN == 'YOUR_BOT_TOKEN' or not config.BOT_TOKEN:
            print("❌ ERROR: Bot token not configured!")
            print("Please set BOT_TOKEN in your .env file or config.py")
            print("Get a token from @BotFather on Telegram: https://t.me/botfather")
            sys.exit(1)
    except ImportError:
        print("❌ ERROR: config.py not found!")
        sys.exit(1)

    print("✅ All checks passed. Starting bot...")
    print("Press Ctrl+C to stop the bot")

    # Import and run the bot
    try:
        import bot
        bot.main()
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

