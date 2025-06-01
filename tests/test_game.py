#!/usr/bin/env python3
"""
Simple test script to verify the Imperial duel game logic works correctly.
Run this to test the core mechanics before deploying the bot.
"""

from game_logic import ImperialDuelGame, Match, Player, GameState
import random

def test_stance_relationships():
    """Test that stance relationships work as expected"""
    game = ImperialDuelGame()
    
    print("=== Testing Stance Relationships ===")
    
    # Test known relationships
    test_cases = [
        ("Bagr", "Radae", "advantage", "disadvantage"),  # Bagr has advantage over Radae
        ("Bagr", "Darda", "advantage", "disadvantage"),  # Bagr has advantage over Darda
        ("Bagr", "Tigr", "neutral", "neutral"),          # Bagr is neutral to Tigr
        ("Bagr", "Riposje", "neutral", "neutral"),       # Bagr is neutral to Riposje
        ("Bagr", "Tortad", "disadvantage", "advantage"), # Bagr has disadvantage vs Tortad
    ]
    
    for stance1, stance2, expected1, expected2 in test_cases:
        result1, result2 = game.get_stance_relationship(stance1, stance2)
        status = "✅" if (result1 == expected1 and result2 == expected2) else "❌"
        print(f"{status} {stance1} vs {stance2}: {result1}/{result2} (expected {expected1}/{expected2})")
    
    print()

def test_adjacency():
    """Test adjacency detection"""
    game = ImperialDuelGame()
    
    print("=== Testing Adjacency ===")
    
    # Test adjacent pairs
    adjacent_pairs = [
        ("Bagr", "Radae"), ("Radae", "Darda"), ("Darda", "Tigr"),
        ("Tigr", "Riposje"), ("Riposje", "Tortad"), ("Tortad", "Bagr")
    ]
    
    for stance1, stance2 in adjacent_pairs:
        is_adj = game.are_stances_adjacent(stance1, stance2)
        status = "✅" if is_adj else "❌"
        print(f"{status} {stance1} - {stance2}: Adjacent = {is_adj}")
    
    # Test opposite pairs
    print("\n--- Opposite Stances ---")
    opposite_pairs = [
        ("Bagr", "Tigr"), ("Radae", "Riposje"), ("Darda", "Tortad")
    ]
    
    for stance1, stance2 in opposite_pairs:
        is_opp = game.are_stances_opposite(stance1, stance2)
        status = "✅" if is_opp else "❌"
        print(f"{status} {stance1} - {stance2}: Opposite = {is_opp}")
    
    print()

def test_dice_rolling():
    """Test dice rolling with advantage/disadvantage"""
    game = ImperialDuelGame()
    
    print("=== Testing Dice Rolling ===")
    
    # Test multiple rolls to see distribution
    for advantage_state in ["advantage", "neutral", "disadvantage"]:
        rolls = []
        for _ in range(10):
            final_roll, all_rolls, used_index = game.roll_dice(advantage_state)
            rolls.append(final_roll)
        
        avg_roll = sum(rolls) / len(rolls)
        print(f"{advantage_state.capitalize()}: {rolls} (avg: {avg_roll:.1f})")
    
    print()

def test_full_round():
    """Test a complete round resolution"""
    game = ImperialDuelGame()
    
    print("=== Testing Full Round ===")
    
    # Create a test match
    player1 = Player(user_id=1, username="Alice")
    player2 = Player(user_id=2, username="Bob")
    
    match = Match(
        channel_id=123,
        player1=player1,
        player2=player2,
        best_of=3,
        adjacency_mod=True  # Enable adjacency mod for testing
    )
    
    # Set up a round
    match.state = GameState.PICKING_STANCES
    match.player1.declared_stances = ["Bagr", "Radae"]
    match.player1.picked_stance = "Bagr"
    match.player2.declared_stances = ["Tigr", "Riposje"]
    match.player2.picked_stance = "Radae"  # Bagr vs Radae = Alice advantage
    
    print(f"Match: {player1.username} ({match.player1.picked_stance}) vs {player2.username} ({match.player2.picked_stance})")
    
    # Resolve the round
    result = game.resolve_round(match)
    
    print(f"Advantage: {result.player1_advantage} vs {result.player2_advantage}")
    print(f"Rolls: {result.player1_roll} vs {result.player2_roll}")
    print(f"Final: {result.player1_final_roll} vs {result.player2_final_roll}")
    
    winner_name = player1.username if result.winner_id == player1.user_id else player2.username
    print(f"Winner: {winner_name}")
    print(f"Score: {match.player1.username} {match.player1.score} - {match.player2.score} {match.player2.username}")
    print(f"Match state: {match.state}")
    
    print()

def test_no_repeat():
    """Test no-repeat rule"""
    game = ImperialDuelGame()
    
    print("=== Testing No-Repeat Rule ===")
    
    # Create match with no-repeat enabled
    player1 = Player(user_id=1, username="Alice")
    player2 = Player(user_id=2, username="Bob")
    
    match = Match(
        channel_id=123,
        player1=player1,
        player2=player2,
        best_of=3,
        no_repeat=True
    )
    
    # Simulate Alice used Bagr last round
    match.last_stances[player1.user_id] = "Bagr"
    
    # Test if Alice can use Bagr again
    can_use_bagr = game.can_use_stance(match, player1.user_id, "Bagr")
    can_use_radae = game.can_use_stance(match, player1.user_id, "Radae")
    
    print(f"Alice used Bagr last round")
    print(f"Can use Bagr again: {can_use_bagr} (should be False)")
    print(f"Can use Radae: {can_use_radae} (should be True)")
    
    print()

def main():
    """Run all tests"""
    print("🎯 Imperial Duel Game Logic Tests")
    print("=" * 40)
    
    # Set random seed for reproducible tests
    random.seed(42)
    
    test_stance_relationships()
    test_adjacency()
    test_dice_rolling()
    test_full_round()
    test_no_repeat()
    
    print("✅ All tests completed!")
    print("\nIf you see any ❌ marks above, there may be issues with the game logic.")
    print("Otherwise, the core mechanics are working correctly!")

if __name__ == "__main__":
    main()
