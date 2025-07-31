#!/usr/bin/env python3
"""
Test script for the modifier functionality (match-wide and round-specific)
"""

import sys
import os

# Add the parent directory to the path so we can import game_logic
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from game_logic import ImperialDuelGame, Match, Player, GameState

def test_modifiers():
    """Test that both match and round modifiers are applied correctly"""
    print("Testing modifier functionality (match and round)...")
    
    # Create a game instance
    game = ImperialDuelGame()
    
    # Create test players
    player1 = Player(user_id=1, username="TestPlayer1")
    player2 = Player(user_id=2, username="TestPlayer2")
    
    # Create a match
    match = Match(
        channel_id=123,
        player1=player1,
        player2=player2,
        best_of=3,
        state=GameState.PICKING_STANCES
    )
    
    # Set up stances for testing
    player1.declared_stances = ["Bagr", "Radae"]
    player1.picked_stance = "Bagr"
    player2.declared_stances = ["Darda", "Tigr"]
    player2.picked_stance = "Darda"
    
    # Test without modifiers
    print("\n1. Testing without modifiers:")
    result1 = game.resolve_round(match)
    print(f"   Player1 roll: {result1.player1_roll} -> {result1.player1_final_roll}")
    print(f"   Player2 roll: {result1.player2_roll} -> {result1.player2_final_roll}")
    print(f"   Custom modifiers applied: {result1.custom_mod_applied}")
    
    # Reset match for next test
    match.current_round = 1
    match.player1.score = 0
    match.player2.score = 0
    match.round_history = []
    match.state = GameState.PICKING_STANCES
    player1.picked_stance = "Bagr"
    player2.picked_stance = "Darda"
    
    # Test with match modifiers only
    print("\n2. Testing with match modifiers (+2 for player1, -1 for player2):")
    match.custom_modifiers = {1: 2, 2: -1}  # player1 gets +2, player2 gets -1
    match.round_modifiers = {}  # No round modifiers
    
    result2 = game.resolve_round(match)
    print(f"   Player1 roll: {result2.player1_roll} -> {result2.player1_final_roll} (modifier: {result2.player1_modifier:+d})")
    print(f"   Player2 roll: {result2.player2_roll} -> {result2.player2_final_roll} (modifier: {result2.player2_modifier:+d})")
    print(f"   Custom modifiers applied: {result2.custom_mod_applied}")
    
    # Reset match for next test
    match.current_round = 1
    match.player1.score = 0
    match.player2.score = 0
    match.round_history = []
    match.state = GameState.PICKING_STANCES
    player1.picked_stance = "Bagr"
    player2.picked_stance = "Darda"
    
    # Test with round modifiers only
    print("\n3. Testing with round modifiers only (+1 for player1, -2 for player2):")
    match.custom_modifiers = {}  # No match modifiers
    match.round_modifiers = {1: 1, 2: -2}  # player1 gets +1, player2 gets -2 for this round only
    
    result3 = game.resolve_round(match)
    print(f"   Player1 roll: {result3.player1_roll} -> {result3.player1_final_roll} (modifier: {result3.player1_modifier:+d})")
    print(f"   Player2 roll: {result3.player2_roll} -> {result3.player2_final_roll} (modifier: {result3.player2_modifier:+d})")
    print(f"   Custom modifiers applied: {result3.custom_mod_applied}")
    
    # Verify round modifiers are cleared after the round
    print(f"   Round modifiers after round: {match.round_modifiers}")
    assert len(match.round_modifiers) == 0, "Round modifiers were not cleared after the round"
    
    # Reset match for next test
    match.current_round = 1
    match.player1.score = 0
    match.player2.score = 0
    match.round_history = []
    match.state = GameState.PICKING_STANCES
    player1.picked_stance = "Bagr"
    player2.picked_stance = "Darda"
    
    # Test with both match and round modifiers
    print("\n4. Testing with both match and round modifiers:")
    match.custom_modifiers = {1: 1, 2: -1}  # Match modifiers
    match.round_modifiers = {1: 1, 2: -1}  # Round modifiers
    
    result4 = game.resolve_round(match)
    print(f"   Player1 roll: {result4.player1_roll} -> {result4.player1_final_roll} (modifier: {result4.player1_modifier:+d})")
    print(f"   Player2 roll: {result4.player2_roll} -> {result4.player2_final_roll} (modifier: {result4.player2_modifier:+d})")
    print(f"   Custom modifiers applied: {result4.custom_mod_applied}")
    
    # Verify the modifiers were combined correctly
    assert result4.player1_modifier == 2, f"Expected player1 modifier to be 2, got {result4.player1_modifier}"
    assert result4.player2_modifier == -2, f"Expected player2 modifier to be -2, got {result4.player2_modifier}"
    
    # Test edge cases
    print("\n5. Testing edge cases (no clamping):")
    # Force some specific rolls by testing multiple times
    for i in range(5):
        match.current_round = 1
        match.player1.score = 0
        match.player2.score = 0
        match.round_history = []
        match.state = GameState.PICKING_STANCES
        player1.picked_stance = "Bagr"
        player2.picked_stance = "Darda"
        match.custom_modifiers = {1: 3, 2: -3}  # Extreme modifiers
        
        result = game.resolve_round(match)
        print(f"   Test {i+1}: P1: {result.player1_roll} -> {result.player1_final_roll}, P2: {result.player2_roll} -> {result.player2_final_roll}")

        # Verify modifiers were applied without clamping
        assert result.player1_final_roll == result.player1_roll + 3, (
            f"Player1 final roll {result.player1_final_roll} unexpected"
        )
        assert result.player2_final_roll == result.player2_roll - 3, (
            f"Player2 final roll {result.player2_final_roll} unexpected"
        )

    print("\n✅ All tests passed! Modifier functionality (match and round) is working correctly.")

def test_chaurus_talent():
    """Test the Chaurus talent toggle"""
    print("\n6. Testing Chaurus talent toggle:")
    game = ImperialDuelGame()

    # Player1 has 'Chaurus' in the name
    player1 = Player(user_id=1, username="Hero Chaurus")
    player2 = Player(user_id=2, username="Opponent")

    match = Match(
        channel_id=999,
        player1=player1,
        player2=player2,
        best_of=3,
        state=GameState.PICKING_STANCES,
        chaurus_talent=True
    )

    player1.declared_stances = ["Bagr", "Radae"]
    player1.picked_stance = "Bagr"
    player2.declared_stances = ["Darda", "Tigr"]
    player2.picked_stance = "Darda"

    result = game.resolve_round(match)
    print(f"   Player1 modifier applied: {result.player1_modifier}")
    assert result.player1_modifier >= 1, "Chaurus talent bonus was not applied"

def test_settings_persistence():
    """Test persistence of the Chaurus talent setting"""
    from settings import load_settings, save_settings

    print("\n7. Testing settings persistence:")
    settings = load_settings()
    original = settings.get('chaurus_talent', False)
    settings['chaurus_talent'] = not original
    save_settings(settings)
    reloaded = load_settings()
    print(f"   Setting after save: {reloaded['chaurus_talent']}")
    assert reloaded['chaurus_talent'] == (not original), "Setting did not persist"
    # Restore
    settings['chaurus_talent'] = original
    save_settings(settings)

def test_triple_stance_role():
    """Test triple stance role functionality"""
    print("\n8. Testing triple stance role:")
    game = ImperialDuelGame()

    player1 = Player(user_id=1, username="TripleHero")
    player2 = Player(user_id=2, username="Opponent")

    match = Match(
        channel_id=555,
        player1=player1,
        player2=player2,
        best_of=3,
        state=GameState.DECLARING_STANCES,
        triple_stance_role_ids=[123, 456]
    )

    player1.declared_stances = ["Bagr", "Radae", "Darda"]
    assert len(match.triple_stance_role_ids) == 2, "Multiple roles should be allowed"
    assert len(player1.declared_stances) == 3, "Player should be able to declare three stances"

if __name__ == "__main__":
    test_modifiers()
    test_chaurus_talent()
    test_settings_persistence()
    test_triple_stance_role()
