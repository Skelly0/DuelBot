# Quick Start Guide

Get your Hex-Duel Discord bot up and running in 5 minutes!

## 1. Prerequisites

- Python 3.11 or higher
- A Discord account
- Basic familiarity with Discord bots

## 2. Setup

### Option A: Automated Setup (Recommended)
```bash
python setup.py
```
This will guide you through the entire setup process.

### Option B: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your bot token
# DISCORD_TOKEN=your_actual_token_here

# Test the game logic
python test_game.py
```

## 3. Create Discord Bot

1. Go to https://discord.com/developers/applications
2. Click "New Application" and give it a name
3. Go to "Bot" section in the sidebar
4. Click "Add Bot" if needed
5. Copy the bot token and add it to your `.env` file
6. Under "Privileged Gateway Intents", you may want to enable "Message Content Intent"

## 4. Invite Bot to Server

1. In the Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes:
   - `bot`
   - `applications.commands`
3. Select bot permissions:
   - Send Messages
   - Use Slash Commands
   - Embed Links
   - Read Message History
4. Copy the generated URL and visit it to invite the bot

## 5. Run the Bot

```bash
python bot.py
```

You should see:
```
Bot has connected to Discord!
Synced slash commands for YourBotName
```

## 6. Test in Discord

In any channel where the bot has permissions:

```
/duel challenge @friend
```

Your friend can then accept with:
```
/duel accept
```

## Commands Quick Reference

| Command | Description |
|---------|-------------|
| `/duel challenge @user` | Start a new duel |
| `/duel accept` | Accept a challenge |
| `/duel stance first second` | Declare two stances |
| `/duel pick choice` | Secret pick (ephemeral) |
| `/duel status` | Show match status |
| `/duel cancel` | Cancel match |

## Example Match

1. **Challenge**: `/duel challenge @bob best_of:3 bait_switch:true`
2. **Accept**: `/duel accept`
3. **Declare**: 
   - Alice: `/duel stance Bagr Tigr`
   - Bob: `/duel stance Radae Tortad`
4. **Optional Switch**: `/duel switch Tigr Darda`
5. **Secret Pick**: 
   - Alice: `/duel pick Bagr` (only Alice sees this)
   - Bob: `/duel pick Radae` (only Bob sees this)
6. **Auto-resolve**: Bot announces results and updates score
7. **Repeat** until someone wins best-of-3

## Troubleshooting

**Bot doesn't respond to commands:**
- Check the bot token is correct
- Ensure bot has proper permissions in the channel
- Make sure you invited with `applications.commands` scope

**Slash commands don't appear:**
- Wait a few minutes for Discord to sync
- Try in a different server
- Restart Discord client

**"No active match" errors:**
- Each channel can only have one active match
- Use `/duel status` to check current state
- Use `/duel cancel` to reset if needed

## Game Rules Summary

**Stances**: Bagr → Radae → Darda → Tigr → Riposje → Tortad (clockwise)

**Advantage**: Each stance beats the next 2 clockwise, loses to 1 counter-clockwise

**Combat**: 
- Advantage = roll 2d6, take higher
- Disadvantage = roll 2d6, take lower  
- Neutral = roll 1d6

**Variants**:
- **No Repeat**: Can't use same stance twice in a row
- **Adjacency Mod**: ±1 for adjacent/opposite stances
- **Bait Switch**: One-time stance swap after declaration

Have fun dueling! 🗡️
