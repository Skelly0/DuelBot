# Custom Modifier Feature

## Overview
The DuelBot now supports custom dice roll modifiers that can be applied by moderators to individual players during a match. This feature allows for dynamic gameplay adjustments and special event scenarios.

## Commands

### `/add_modifier @player modifier`
- **Permission Required**: Manage Messages (moderator)
- **Parameters**:
  - `@player`: The player to apply the modifier to (must be part of the current match)
  - `modifier`: Integer value between -3 and +3
- **Usage**: Adds a persistent dice roll modifier to the specified player
- **Timing**: Can only be used after both players have made their first declaration

### `/view_modifiers`
- **Permission Required**: Manage Messages (moderator)
- **Usage**: Shows all active modifiers in the current match
- **Response**: Ephemeral (only visible to the moderator who used the command)

## How It Works

1. **Application**: Modifiers are applied to the final dice roll after all other calculations (advantage/disadvantage, adjacency modifiers)
2. **Range**: Modifiers are clamped to ensure final rolls stay within 1-6 bounds
3. **Persistence**: Modifiers remain active for the entire match until changed or removed
4. **Removal**: Set a modifier to 0 to remove it
5. **Display**: Active modifiers are shown in round result footers

## Examples

```
/add_modifier @Alice +2    # Alice gets +2 to all dice rolls
/add_modifier @Bob -1      # Bob gets -1 to all dice rolls
/add_modifier @Alice 0     # Removes Alice's modifier
/view_modifiers            # Shows current modifiers
```

## Technical Details

- Modifiers are stored in the `Match.custom_modifiers` dictionary
- Applied in `ImperialDuelGame.resolve_round()` after adjacency modifiers
- Tracked in `RoundResult` for display purposes
- Bounds checking ensures rolls stay within 1-6 range

## Use Cases

- **Event Matches**: Special tournament conditions
- **Balancing**: Temporary adjustments for skill differences
- **Storytelling**: Narrative elements (curses, blessings, etc.)
- **Testing**: Debugging and balance testing
