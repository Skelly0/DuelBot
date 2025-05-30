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
    round_history: List[RoundResult] = field(default_factory=list)
    last_stances: Dict[int, str] = field(default_factory=dict)  # user_id -> last stance used
    custom_modifiers: Dict[int, int] = field(default_factory=dict)  # user_id -> modifier value

class ImperialDuelGame:
    STANCES = ["Bagr", "Radae", "Darda", "Tigr", "Riposje", "Tortad"]
    
    def __init__(self):
        # Pre-compute stance relationships
        self.stance_to_index = {stance: i for i, stance in enumerate(self.STANCES)}
        
    def get_stance_relationship(self, stance1: str, stance2: str) -> Tuple[str, str]:
        """
        Returns advantage state for (stance1, stance2)
        Returns: (stance1_advantage, stance2_advantage)
        """
        idx1 = self.stance_to_index[stance1]
        idx2 = self.stance_to_index[stance2]
        
        # Calculate delta: (idx2 - idx1) mod 6
        delta = (idx2 - idx1) % 6
        
        if delta in [1, 2]:
            # stance1 has advantage over stance2
            return "advantage", "disadvantage"
        elif delta == 5:
            # stance1 has disadvantage vs stance2 (only delta 5, not 4)
            return "disadvantage", "advantage"
        else:
            # neutral (delta == 0, 3, or 4)
            return "neutral", "neutral"
    
    def are_stances_adjacent(self, stance1: str, stance2: str) -> bool:
        """Check if two stances are adjacent on the hexagon"""
        idx1 = self.stance_to_index[stance1]
        idx2 = self.stance_to_index[stance2]
        delta = abs(idx1 - idx2)
        return delta == 1 or delta == 5
    
    def are_stances_opposite(self, stance1: str, stance2: str) -> bool:
        """Check if two stances are opposite on the hexagon"""
        idx1 = self.stance_to_index[stance1]
        idx2 = self.stance_to_index[stance2]
        delta = abs(idx1 - idx2)
        return delta == 3
    
    def roll_dice(self, advantage_state: str) -> Tuple[int, List[int]]:
        """
        Roll dice based on advantage state
        Returns: (final_roll, all_rolls)
        """
        if advantage_state == "advantage":
            rolls = [random.randint(1, 6), random.randint(1, 6)]
            return max(rolls), rolls
        elif advantage_state == "disadvantage":
            rolls = [random.randint(1, 6), random.randint(1, 6)]
            return min(rolls), rolls
        else:  # neutral
            roll = random.randint(1, 6)
            return roll, [roll]
    
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
        
        # Roll dice
        p1_roll, p1_all_rolls = self.roll_dice(p1_adv)
        p2_roll, p2_all_rolls = self.roll_dice(p2_adv)
        
        # Apply adjacency modifier if enabled
        adjacency_applied = False
        if match.adjacency_mod:
            p1_final = self.apply_adjacency_mod(p1_roll, p1_stance, p2_stance)
            p2_final = self.apply_adjacency_mod(p2_roll, p2_stance, p1_stance)
            adjacency_applied = (p1_final != p1_roll) or (p2_final != p2_roll)
        else:
            p1_final = p1_roll
            p2_final = p2_roll
        
        # Apply custom modifiers if any
        p1_modifier = match.custom_modifiers.get(match.player1.user_id, 0)
        p2_modifier = match.custom_modifiers.get(match.player2.user_id, 0)
        custom_mod_applied = p1_modifier != 0 or p2_modifier != 0
        
        if p1_modifier != 0:
            p1_final = max(1, min(6, p1_final + p1_modifier))
        if p2_modifier != 0:
            p2_final = max(1, min(6, p2_final + p2_modifier))
        
        # Determine winner
        if p1_final > p2_final:
            winner_id = match.player1.user_id
            match.player1.score += 1
        elif p2_final > p1_final:
            winner_id = match.player2.user_id
            match.player2.score += 1
        else:
            # Tie - could implement tiebreaker rules here
            winner_id = match.player1.user_id  # Default to player1 for now
            match.player1.score += 1
        
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
            player2_modifier=p2_modifier
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
        
        return result
    
    def can_use_stance(self, match: Match, user_id: int, stance: str) -> bool:
        """Check if a player can use a stance (considering no_repeat rule)"""
        if not match.no_repeat:
            return True
        
        last_stance = match.last_stances.get(user_id)
        return last_stance != stance
    
    def validate_stance(self, stance: str) -> bool:
        """Validate if a stance name is valid"""
        return stance in self.STANCES
