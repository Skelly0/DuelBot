#!/usr/bin/env python3
"""
Setup script for the Imperial Duel Discord Bot.
This script helps users set up the bot environment and check dependencies.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 11):
        print(f"❌ Python 3.11+ required, but you have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import discord
        print(f"✅ discord.py {discord.__version__}")
        
        # Check discord.py version
        version_parts = discord.__version__.split('.')
        major, minor = int(version_parts[0]), int(version_parts[1])
        if major < 2 or (major == 2 and minor < 4):
            print(f"⚠️  discord.py 2.4+ recommended, you have {discord.__version__}")
        
    except ImportError:
        print("❌ discord.py not installed")
        return False
    
    try:
        import dotenv
        print("✅ python-dotenv installed")
    except ImportError:
        print("❌ python-dotenv not installed")
        return False
    
    return True

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def setup_env_file():
    """Help user set up .env file"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example_path.exists():
        print("❌ .env.example file not found")
        return False
    
    print("\n🔧 Setting up .env file...")
    
    # Copy .env.example to .env
    with open(env_example_path, 'r') as f:
        content = f.read()
    
    print("Please provide your Discord bot token:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Create a new application or select existing one")
    print("3. Go to 'Bot' section and copy the token")
    print()
    
    token = input("Enter your Discord bot token: ").strip()
    
    if not token:
        print("❌ No token provided")
        return False
    
    # Replace placeholder with actual token
    content = content.replace("your_bot_token_here", token)
    
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ .env file created successfully!")
    return True

def test_game_logic():
    """Run game logic tests"""
    print("\n🧪 Testing game logic...")
    try:
        import tests.test_game as test_game
        test_game.main()
        return True
    except Exception as e:
        print(f"❌ Game logic test failed: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Invite your bot to a Discord server:")
    print("   - Go to https://discord.com/developers/applications")
    print("   - Select your application > OAuth2 > URL Generator")
    print("   - Select 'bot' and 'applications.commands' scopes")
    print("   - Select necessary permissions (Send Messages, Use Slash Commands)")
    print("   - Copy and visit the generated URL")
    print()
    print("2. Run the bot:")
    print("   python bot.py")
    print()
    print("3. Test in Discord:")
    print("   /duel challenge @someone")
    print()
    print("📖 See README.md for full documentation!")

def main():
    """Main setup function"""
    print("🎯 Imperial Duel Discord Bot Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        print("\nPlease upgrade to Python 3.11 or higher and try again.")
        return False
    
    # Check if dependencies are installed
    deps_ok = check_dependencies()
    
    if not deps_ok:
        print("\n📦 Installing missing dependencies...")
        if not install_dependencies():
            return False
        
        # Check again after installation
        if not check_dependencies():
            print("❌ Dependencies still missing after installation")
            return False
    
    # Set up .env file
    if not setup_env_file():
        print("\n⚠️  You'll need to manually create a .env file with your bot token")
        print("See .env.example for the format")
    
    # Test game logic
    if not test_game_logic():
        print("⚠️  Game logic tests failed, but you can still try running the bot")
    
    show_next_steps()
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
