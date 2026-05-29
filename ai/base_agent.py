from abc import ABC, abstractmethod
from typing import List
from svwb_ai.engine.game_state import GameState
from svwb_ai.engine.action import Action


class BaseAgent(ABC):
    """Base class for all agents"""

    @abstractmethod
    def get_action(self, state: GameState, legal_actions: List[Action]) -> Action:
        """
        Get the action to take in the current state.

        Args:
            state: Current game state
            legal_actions: List of legal actions available

        Returns:
            The action to take
        """
        pass
