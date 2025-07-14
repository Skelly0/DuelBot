from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random

class GameState(Enum):
    WAITING_FOR_ACCEPT = "waiting_for_accept"
    DECLARING_STANCES = "declaring_stances"
    PICKING_STANCES = "picking_stances"
    ROUND_COMPLETE = "round_complete"
    MATCH_COMPLETE = "match_complete"

@dataclass
class Player:
    user_id: int
    username: str
    declared_stances: List[str] = field(default_factory=list)
    picked_stance: Optional[str] = None
    has_switched: bool = False
    score: int = 0

@dataclass
class RoundResult:
    player1_stance: str
    player2_stance: str
    player1_roll: int
    player2_roll: int
    player1_advantage: str  # "advantage", "disadvantage", "neutral"
    player2_advantage: str
    winner_id: int
    adjacency_mod_applied: bool = False
    player1_final_roll: int = 0
    player2_final_roll: int = 0
    custom_mod_applied: bool = False
    player1_modifier: int = 0
    player2_modifier: int = 0
    player1_all_rolls: List[int] = field(default_factory=list)
    player2_all_rolls: List[int] = field(default_factory=list)
    player1_used_roll_index: int = -1
    player2_used_roll_index: int = -1
    tie_rerolled: bool = False
    initial_player1_roll: int = 0
    initial_player2_roll: int = 0
    initial_player1_final_roll: int = 0
    initial_player2_final_roll: int = 0
    initial_player1_all_rolls: List[int] = field(default_factory=list)
    initial_player2_all_rolls: List[int] = field(default_factory=list)
    initial_player1_used_roll_index: int = -1
    initial_player2_used_roll_index: int = -1

@dataclass
class Match:
    channel_id: int
    player1: Player
    player2: Player
    best_of: int
    state: GameState = GameState.WAITING_FOR_ACCEPT
    current_round: int = 1
    no_repeat: bool = False
    adjacency_mod: bool = False
    bait_switch: bool = False
    chaurus_talent: bool = False
    triple_stance_word: str = ''
    round_history: List[RoundResult] = field(default_factory=list)
    last_stances: Dict[int, str] = field(default_factory=dict)  # user_id -> last stance used
    custom_modifiers: Dict[int, int] = field(default_factory=dict)  # user_id -> modifier value (match-wide)
    round_modifiers: Dict[int, int] = field(default_factory=dict)  # user_id -> modifier value (current round only)

class ImperialDuelGame:
    STANCES = ["Bagr", "Radae", "Darda", "Tigr", "Riposje", "Tortad"]

    def __init__(self):
        # Pre-compute stance relationships
        # Use lowercase keys for lookups so stance names are case-insensitive
        self.stance_to_index = {stance.lower(): i for i, stance in enumerate(self.STANCES)}
        
    def get_stance_relationship(self, stance1: str, stance2: str) -> Tuple[str, str]:
        """
        Returns advantage state for (stance1, stance2)
        Returns: (stance1_advantage, stance2_advantage)
        """
        # Normalize input for case/whitespace inconsistencies
        stance1 = stance1.strip().lower()
        stance2 = stance2.strip().lower()

        idx1 = self.stance_to_index[stance1]
        idx2 = self.stance_to_index[stance2]
        
        # Calculate delta: (idx2 - idx1) mod 6
        delta = (idx2 - idx1) % 6

        if delta in [1, 2]:
            # stance1 has advantage over stance2
            return "advantage", "disadvantage"
        elif delta == 5:
            # stance1 has disadvantage vs stance2 (counter-clockwise adjacent)
            return "disadvantage", "advantage"
        elif delta == 4:
            # stance2 has advantage over stance1 while stance1 remains neutral
            return "neutral", "advantage"
        else:
            # neutral (delta == 0 or 3)
            return "neutral", "neutral"
    
    def are_stances_adjacent(self, stance1: str, stance2: str) -> bool:
        """Check if two stances are adjacent on the hexagon"""
        stance1 = stance1.strip().lower()
        stance2 = stance2.strip().lower()
        idx1 = self.stance_to_index[stance1]
        idx2 = self.stance_to_index[stance2]
        delta = abs(idx1 - idx2)
        return delta == 1 or delta == 5
    
    def are_stances_opposite(self, stance1: str, stance2: str) -> bool:
        """Check if two stances are opposite on the hexagon"""
        stance1 = stance1.strip().lower()
        stance2 = stance2.strip().lower()
        idx1 = self.stance_to_index[stance1]
        idx2 = self.stance_to_index[stance2]
        delta = abs(idx1 - idx2)
        return delta == 3
    
    def roll_dice(self, advantage_state: str) -> Tuple[int, List[int], int]:
        """
        Roll dice based on advantage state
        Returns: (final_roll, all_rolls, used_roll_index)
        used_roll_index: -1 for single roll, 0/1 for which roll was used in advantage/disadvantage
        """
        if advantage_state == "advantage":
            rolls = [random.randint(1, 6), random.randint(1, 6)]
            max_roll = max(rolls)
            used_index = rolls.index(max_roll)
            return max_roll, rolls, used_index
        elif advantage_state == "disadvantage":
            rolls = [random.randint(1, 6), random.randint(1, 6)]
            min_roll = min(rolls)
            used_index = rolls.index(min_roll)
            return min_roll, rolls, used_index
        else:  # neutral
            roll = random.randint(1, 6)
            return roll, [roll], -1
    
    def apply_adjacency_mod(self, roll: int, stance1: str, stance2: str) -> int:
        """Apply adjacency modifier to roll"""
        if self.are_stances_adjacent(stance1, stance2):
            return max(1, min(6, roll + 1))
        elif self.are_stances_opposite(stance1, stance2):
            return max(1, min(6, roll - 1))
        return roll
    
    def resolve_round(self, match: Match) -> RoundResult:
        """Resolve a round and return the result"""
        p1_stance = match.player1.picked_stance
        p2_stance = match.player2.picked_stance
        
        # Get advantage states
        p1_adv, p2_adv = self.get_stance_relationship(p1_stance, p2_stance)
        
        # Pre-compute modifiers that persist across rerolls
        p1_match_modifier = match.custom_modifiers.get(match.player1.user_id, 0)
        p2_match_modifier = match.custom_modifiers.get(match.player2.user_id, 0)

        p1_round_modifier = match.round_modifiers.get(match.player1.user_id, 0)
        p2_round_modifier = match.round_modifiers.get(match.player2.user_id, 0)

        p1_modifier = p1_match_modifier + p1_round_modifier
        p2_modifier = p2_match_modifier + p2_round_modifier

        if match.chaurus_talent:
            if "chaurus" in match.player1.username.lower():
                p1_modifier += 1
            if "chaurus" in match.player2.username.lower():
                p2_modifier += 1

        custom_mod_applied = p1_modifier != 0 or p2_modifier != 0

        # Roll dice with rerolls until a winner is determined
        tie_rerolled = False
        first_p1_roll = first_p2_roll = None
        first_p1_all = first_p2_all = None
        first_p1_index = first_p2_index = -1
        first_p1_final = first_p2_final = 0
        first_iteration = True
        while True:
            p1_roll, p1_all_rolls, p1_used_index = self.roll_dice(p1_adv)
            p2_roll, p2_all_rolls, p2_used_index = self.roll_dice(p2_adv)

            adjacency_applied = False
            if match.adjacency_mod:
                p1_final = self.apply_adjacency_mod(p1_roll, p1_stance, p2_stance)
                p2_final = self.apply_adjacency_mod(p2_roll, p2_stance, p1_stance)
                adjacency_applied = (p1_final != p1_roll) or (p2_final != p2_roll)
            else:
                p1_final = p1_roll
                p2_final = p2_roll

            if p1_modifier != 0:
                p1_final = p1_final + p1_modifier
            if p2_modifier != 0:
                p2_final = p2_final + p2_modifier

            if first_iteration:
                first_p1_roll = p1_roll
                first_p2_roll = p2_roll
                first_p1_all = p1_all_rolls
                first_p2_all = p2_all_rolls
                first_p1_index = p1_used_index
                first_p2_index = p2_used_index
                first_p1_final = p1_final
                first_p2_final = p2_final
                first_iteration = False

            if p1_final != p2_final:
                break

            tie_rerolled = True
        
        
        # Determine winner (loop guarantees no tie)
        if p1_final > p2_final:
            winner_id = match.player1.user_id
            match.player1.score += 1
        else:
            winner_id = match.player2.user_id
            match.player2.score += 1
        
        # Update last stances for no_repeat rule
        if match.no_repeat:
            match.last_stances[match.player1.user_id] = p1_stance
            match.last_stances[match.player2.user_id] = p2_stance
        
        result = RoundResult(
            player1_stance=p1_stance,
            player2_stance=p2_stance,
            player1_roll=p1_roll,
            player2_roll=p2_roll,
            player1_advantage=p1_adv,
            player2_advantage=p2_adv,
            winner_id=winner_id,
            adjacency_mod_applied=adjacency_applied,
            player1_final_roll=p1_final,
            player2_final_roll=p2_final,
            custom_mod_applied=custom_mod_applied,
            player1_modifier=p1_modifier,
            player2_modifier=p2_modifier,
            player1_all_rolls=p1_all_rolls,
            player2_all_rolls=p2_all_rolls,
            player1_used_roll_index=p1_used_index,
            player2_used_roll_index=p2_used_index,
            tie_rerolled=tie_rerolled,
            initial_player1_roll=first_p1_roll if tie_rerolled else p1_roll,
            initial_player2_roll=first_p2_roll if tie_rerolled else p2_roll,
            initial_player1_final_roll=first_p1_final if tie_rerolled else p1_final,
            initial_player2_final_roll=first_p2_final if tie_rerolled else p2_final,
            initial_player1_all_rolls=first_p1_all if tie_rerolled else p1_all_rolls,
            initial_player2_all_rolls=first_p2_all if tie_rerolled else p2_all_rolls,
            initial_player1_used_roll_index=first_p1_index if tie_rerolled else p1_used_index,
            initial_player2_used_roll_index=first_p2_index if tie_rerolled else p2_used_index
        )
        
        match.round_history.append(result)
        
        # Check if match is complete
        wins_needed = (match.best_of + 1) // 2
        if match.player1.score >= wins_needed or match.player2.score >= wins_needed:
            match.state = GameState.MATCH_COMPLETE
        else:
            match.current_round += 1
            match.state = GameState.DECLARING_STANCES
            # Reset for next round
            match.player1.declared_stances = []
            match.player1.picked_stance = None
            match.player1.has_switched = False
            match.player2.declared_stances = []
            match.player2.picked_stance = None
            match.player2.has_switched = False
            
            # Clear round-specific modifiers
            match.round_modifiers.clear()
        
        return result
    
    def can_use_stance(self, match: Match, user_id: int, stance: str) -> bool:
        """Check if a player can use a stance (considering no_repeat rule)"""
        if not match.no_repeat:
            return True
        
        last_stance = match.last_stances.get(user_id)
        return last_stance != stance
    
    def validate_stance(self, stance: str) -> bool:
        """Validate if a stance name is valid (case-insensitive)"""
        return stance.strip().lower() in self.stance_to_index
