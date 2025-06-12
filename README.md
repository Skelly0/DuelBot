# Duel Discord Bot

A Discord bot that runs the six-stance dueling mini-game via slash commands, handling match flow, hidden picks, dice rolls with advantage/disadvantage, and scoring.

## Features

- **Six-stance combat system**: Bagr, Radae, Darda, Tigr, Riposje, Tortad arranged in a hexagon
- **Advantage/disadvantage mechanics**: Based on stance relationships with dice rolling
- **Hidden picks**: Players declare two stances publicly, then secretly pick one
- **Optional variants**:
  - No Repeat: Forbid using the same stance twice in a row
  - Adjacency Mod: +1/-1 modifier for adjacent/opposite stances
  - Bait & Switch: One-time stance switching after declaration

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Discord bot**:
   - Go to https://discord.com/developers/applications
   - Create a new application and bot
   - Copy the bot token

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your DISCORD_TOKEN
   ```

4. **Invite bot to server**:
   - Generate invite URL with `applications.commands` scope
   - Ensure bot has permission to send messages and use slash commands

5. **Run the bot**:
   ```bash
   python bot.py
   ```

## Commands

### `/duel challenge @opponent [options]`
Start a new duel challenge.
- `opponent`: The player to challenge
- `best_of`: Best of 3, 5, or 7 rounds (default: 3)
- `no_repeat`: Forbid using same stance twice in a row
- `adjacency_mod`: Apply +1/-1 modifier for adjacent/opposite stances
- `bait_switch`: Allow one-time stance switching after declaration

### `/duel accept`
Accept a pending challenge (challenged player only).

### `/duel stance first second`
Declare two possible stances for the round (public).

### `/duel pick choice`
Secretly pick one of your declared stances (ephemeral).

### `/duel switch old new`
Switch one declared stance for another (if bait_switch enabled).

### `/duel status`
Show current match status, scores, and what's needed next.

### `/duel cancel`
Cancel the current match (requires confirmation).

### `/duel end`
Force-end a match (moderators only).

## Game Rules

### Stance Relationships
The six stances are arranged clockwise around a hexagon:
**Bagr → Radae → Darda → Tigr → Riposje → Tortad → Bagr**

Each stance has:
- **Advantage** over the next 2 stances clockwise
- **Neutral** against the following 2 stances
- **Disadvantage** against the 1 stance counter-clockwise

### Combat Resolution
1. Players declare two stances publicly
2. Players secretly pick one of their declared stances
3. Bot determines advantage/disadvantage based on stance matchup
4. Each player rolls 1d6:
   - **Advantage**: Roll twice, take higher
   - **Disadvantage**: Roll twice, take lower
   - **Neutral**: Roll once
5. Apply adjacency modifier if enabled:
   - **Adjacent stances**: +1 to roll
   - **Opposite stances**: -1 to roll
6. Higher roll wins the round
7. First to required wins takes the match

### Optional Variants

**No Repeat**: Players cannot use the same stance they used in the previous round.

**Adjacency Mod**: Rolls are modified based on stance positions:
- Adjacent stances (1 position apart): +1 to roll
- Opposite stances (3 positions apart): -1 to roll

**Bait & Switch**: After both players declare their stances, each player gets one opportunity to publicly switch one of their declared stances before making their secret pick.

## File Structure

- `bot.py`: Main Discord bot with slash commands
- `game_logic.py`: Core game mechanics and match state management
- `requirements.txt`: Python dependencies
- `.env.example`: Environment variable template
- `README.md`: This file

## Development

The bot uses:
- **discord.py 2.4+** for Discord integration
- **python-dotenv** for environment variable management
- **dataclasses** for clean state management
- **asyncio** for async Discord operations

Match state is stored in memory and cleaned up when matches complete. For persistence across bot restarts, consider adding Redis or database storage.

## Example Match Flow

1. Alice challenges Bob: `/duel challenge @Bob best_of:5 bait_switch:true`
2. Bob accepts: `/duel accept`
3. Round 1 begins - both players declare stances:
   - Alice: `/duel stance Bagr Tigr`
   - Bob: `/duel stance Radae Tortad`
4. Optional bait & switch:
   - Alice: `/duel switch Tigr Darda`
5. Secret picks:
   - Alice: `/duel pick Bagr` (ephemeral)
   - Bob: `/duel pick Radae` (ephemeral)
6. Bot resolves: Bagr vs Radae → Alice has advantage, rolls 2d6 take higher
7. Continue until one player reaches 3 wins (best of 5)

## Troubleshooting

- **Bot not responding**: Check token is correct and bot has proper permissions
- **Slash commands not appearing**: Ensure bot was invited with `applications.commands` scope
- **Commands failing**: Check bot has permission to send messages in the channel
