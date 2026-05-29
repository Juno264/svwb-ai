from typing import List
from svwb_ai.engine.game_state import GameState
from svwb_ai.engine.action import Action, ActionType
from svwb_ai.ai.base_agent import BaseAgent


class RuleAgent(BaseAgent):
    """
    Rule-based agent using heuristic strategy.
    For Phase 1: Focuses on low-cost plays and simple attacks.
    """

    def get_action(self, state: GameState, legal_actions: List[Action]) -> Action:
        """
        Select action based on heuristic rules:
        1. Play low-cost cards (fill board)
        2. Attack if beneficial
        3. End turn if no good plays
        """
        if not legal_actions:
            return Action(ActionType.END_TURN)

        player = state.active_player
        opponent = state.opponent_player

        # Separate actions by type
        play_actions = [a for a in legal_actions if a.action_type == ActionType.PLAY_CARD]
        attack_actions = [a for a in legal_actions if a.action_type == ActionType.ATTACK]
        evolve_actions = [a for a in legal_actions if a.action_type == ActionType.EVOLVE]
        end_turn_action = next((a for a in legal_actions if a.action_type == ActionType.END_TURN), None)

        # Heuristic 1: Play low-cost cards first
        if play_actions:
            # Sort by cost (ascending)
            best_play = min(play_actions, key=lambda a: player.hand[a.card_index].cost)
            return best_play

        # Heuristic 2: Attack opponent's leader if we have strong followers
        leader_attacks = [a for a in attack_actions if a.target_is_leader]
        if leader_attacks:
            # Attack with strongest follower
            best_attack = max(leader_attacks, key=lambda a: player.board[a.attacker_index].card.attack)
            return best_attack

        # Heuristic 3: Attack opponent's followers if beneficial
        if attack_actions:
            return attack_actions[0]

        # Heuristic 4: Evolve if possible
        if evolve_actions:
            return evolve_actions[0]

        # Default: End turn
        return end_turn_action or Action(ActionType.END_TURN)
