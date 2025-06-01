# Dice Roll Modifiers Feature

## Overview
The DuelBot supports dice roll modifiers that can be applied by moderators to individual players during a match. Two types of modifiers are available:

1. **Round Modifiers**: Apply only for the current round
2. **Match Modifiers**: Apply for the entire match

This feature allows for dynamic gameplay adjustments and special event scenarios.

## Commands

### `/add_round_modifier @player modifier`
- **Permission Required**: Manage Messages (moderator)
- **Parameters**:
  - `@player`: The player to apply the modifier to (must be part of the current match)
  - `modifier`: Integer value between -3 and +3
- **Usage**: Adds a dice roll modifier to the specified player for the current round only
- **Timing**: Can only be used after both players have made their first declaration
- **Duration**: Automatically cleared after the round ends

### `/add_match_modifier @player modifier`
- **Permission Required**: Manage Messages (moderator)
- **Parameters**:
  - `@player`: The player to apply the modifier to (must be part of the current match)
  - `modifier`: Integer value between -3 and +3
- **Usage**: Adds a persistent dice roll modifier to the specified player for the entire match
- **Timing**: Can only be used after both players have made their first declaration
- **Duration**: Remains active until the match ends or is explicitly removed

### `/view_modifiers`
- **Permission Required**: Manage Messages (moderator)
- **Usage**: Shows all active modifiers (both round and match) in the current match
- **Response**: Ephemeral (only visible to the moderator who used the command)

## How It Works

1. **Application**: Modifiers are applied to the final dice roll after all other calculations (advantage/disadvantage, adjacency modifiers)
2. **Stacking**: Round and match modifiers stack with each other (e.g., a +1 round modifier and a +1 match modifier result in a +2 total modifier)
3. **Range**: Modifiers are clamped to ensure final rolls stay within 1-6 bounds
4. **Persistence**:
   - Round modifiers are automatically cleared after each round
   - Match modifiers remain active for the entire match until changed or removed
5. **Removal**: Set a modifier to 0 to remove it
6. **Display**: Active modifiers are shown in round result footers

## Examples

```
/add_round_modifier @Alice +2    # Alice gets +2 to dice rolls for this round only
/add_match_modifier @Bob -1      # Bob gets -1 to all dice rolls for the entire match
/add_round_modifier @Alice 0     # Removes Alice's round modifier
/add_match_modifier @Bob 0       # Removes Bob's match modifier
/view_modifiers                  # Shows current modifiers
```

## Technical Details

- Round modifiers are stored in the `Match.round_modifiers` dictionary and cleared after each round
- Match modifiers are stored in the `Match.custom_modifiers` dictionary and persist for the entire match
- Both types of modifiers are applied in `ImperialDuelGame.resolve_round()` after adjacency modifiers
- Tracked in `RoundResult` for display purposes
- Bounds checking ensures rolls stay within 1-6 range

## Use Cases

- **Event Matches**: Special tournament conditions
- **Balancing**: Temporary adjustments for skill differences
- **Storytelling**: Narrative elements (curses, blessings, etc.)
- **Tactical Adjustments**: Round modifiers for specific tactical situations
- **Penalties/Rewards**: Round modifiers as penalties or rewards for specific actions
- **Testing**: Debugging and balance testing
