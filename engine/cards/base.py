from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from svwb_ai.engine.game_state import GameState


class Keyword:
    """Marker for keywords/abilities"""
    pass


@dataclass
class CardInstance:
    """Represents a card instance (in hand, board, graveyard)"""
    card_id: str
    name: str
    cost: int
    card_type: 'CardType'
    spell_boost_count: int = 0  # Spell Boost counter

    # Follower-only fields
    attack: int = 0
    hp: int = 0
    evolved: bool = False
    super_evolved: bool = False
    summoning_sick: bool = True  # Can't attack on turn summoned
    exhausted: bool = False  # Has attacked this turn
    keywords: frozenset[str] = field(default_factory=frozenset)

    # Amulet-only fields
    countdown: Optional[int] = None

    def copy(self):
        """Create a copy of this card instance"""
        from copy import deepcopy
        return deepcopy(self)


class BaseCard(ABC):
    """Base class for all cards - subclasses override effect methods"""

    def __init__(self, card_id: str, name: str, cost: int, card_type: str):
        self.card_id = card_id
        self.name = name
        self.cost = cost
        self.card_type = card_type

    def create_instance(self) -> CardInstance:
        """Create a new instance of this card"""
        return CardInstance(
            card_id=self.card_id,
            name=self.name,
            cost=self.cost,
            card_type=self.card_type,
        )

    def on_fanfare(self, state: 'GameState', player_idx: int, card: CardInstance,
                   targets: list = None) -> 'GameState':
        """Called when card is played (fanfare effect)"""
        return state

    def on_last_word(self, state: 'GameState', player_idx: int, card: CardInstance) -> 'GameState':
        """Called when follower is destroyed (last word effect)"""
        return state

    def on_evolve(self, state: 'GameState', player_idx: int, card: CardInstance) -> 'GameState':
        """Called when follower evolves"""
        return state

    def on_super_evolve(self, state: 'GameState', player_idx: int, card: CardInstance) -> 'GameState':
        """Called when follower super evolves (also triggers evolve effects)"""
        return self.on_evolve(state, player_idx, card)

    def on_turn_end(self, state: 'GameState', player_idx: int, card: CardInstance) -> 'GameState':
        """Called at end of turn (for amulets, etc.)"""
        return state

    def on_turn_start(self, state: 'GameState', player_idx: int, card: CardInstance) -> 'GameState':
        """Called at start of turn"""
        return state


class FollowerCard(BaseCard):
    """Base class for follower cards"""

    def __init__(self, card_id: str, name: str, cost: int, attack: int, hp: int):
        super().__init__(card_id, name, cost, 'FOLLOWER')
        self.attack = attack
        self.hp = hp

    def create_instance(self) -> CardInstance:
        instance = super().create_instance()
        instance.attack = self.attack
        instance.hp = self.hp
        return instance


class SpellCard(BaseCard):
    """Base class for spell cards"""

    def __init__(self, card_id: str, name: str, cost: int):
        super().__init__(card_id, name, cost, 'SPELL')


class AmuletCard(BaseCard):
    """Base class for amulet cards"""

    def __init__(self, card_id: str, name: str, cost: int, countdown: int = 0):
        super().__init__(card_id, name, cost, 'AMULET')
        self.countdown = countdown

    def create_instance(self) -> CardInstance:
        instance = super().create_instance()
        instance.countdown = self.countdown
        return instance

    def on_activate(self, state: 'GameState', player_idx: int, card: CardInstance) -> 'GameState':
        """Called when amulet countdown reaches 0"""
        return state
