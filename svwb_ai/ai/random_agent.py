import random
from typing import List
from svwb_ai.engine.game_state import GameState
from svwb_ai.engine.action import Action, ActionType
from svwb_ai.ai.base_agent import BaseAgent


class RandomAgent(BaseAgent):
    """Agent that plays random legal actions"""

    def get_action(self, state: GameState, legal_actions: List[Action]) -> Action:
        """Return a random legal action"""
        if not legal_actions:
            return Action(ActionType.END_TURN)
        return random.choice(legal_actions)
