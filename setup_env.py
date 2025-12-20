#!/usr/bin/env python3
"""
Setup script to configure environment variables for the Divar Search Bot
"""

import os
import shutil

def setup_environment():
    """Setup the .env file from env.example"""
    env_file = '.env'
    env_example = 'env.example'

    print("🔧 Setting up environment configuration...")

    # Check if .env already exists
    if os.path.exists(env_file):
        response = input(f"⚠️  {env_file} already exists. Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("✅ Keeping existing configuration.")
            return

    # Check if env.example exists
    if not os.path.exists(env_example):
        print(f"❌ Error: {env_example} not found!")
        return

    # Copy env.example to .env
    try:
        shutil.copy2(env_example, env_file)
        print(f"✅ Created {env_file} from {env_example}")
        print("\n📝 Next steps:")
        print(f"1. Edit {env_file} and set your BOT_TOKEN")
        print("2. Get your bot token from @BotFather on Telegram")
        print("3. Run the bot with: docker-compose up -d")
        print("\n🔗 @BotFather: https://t.me/botfather")

    except Exception as e:
        print(f"❌ Error creating {env_file}: {e}")

if __name__ == "__main__":
    setup_environment()




