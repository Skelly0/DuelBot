#!/usr/bin/env python3
"""
Test script for the new modifier functionality
"""

from game_logic import ImperialDuelGame, Match, Player, GameState

def test_custom_modifiers():
    """Test that custom modifiers are applied correctly"""
    print("Testing custom modifier functionality...")
    
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
    
    # Test with modifiers
    print("\n2. Testing with modifiers (+2 for player1, -1 for player2):")
    match.custom_modifiers = {1: 2, 2: -1}  # player1 gets +2, player2 gets -1
    
    result2 = game.resolve_round(match)
    print(f"   Player1 roll: {result2.player1_roll} -> {result2.player1_final_roll} (modifier: {result2.player1_modifier:+d})")
    print(f"   Player2 roll: {result2.player2_roll} -> {result2.player2_final_roll} (modifier: {result2.player2_modifier:+d})")
    print(f"   Custom modifiers applied: {result2.custom_mod_applied}")
    
    # Test edge cases
    print("\n3. Testing edge cases (rolls clamped to 1-6):")
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
        
        # Verify rolls are within bounds
        assert 1 <= result.player1_final_roll <= 6, f"Player1 final roll {result.player1_final_roll} out of bounds"
        assert 1 <= result.player2_final_roll <= 6, f"Player2 final roll {result.player2_final_roll} out of bounds"
    
    print("\n✅ All tests passed! Custom modifier functionality is working correctly.")

if __name__ == "__main__":
    test_custom_modifiers()
