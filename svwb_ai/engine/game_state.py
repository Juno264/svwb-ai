from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from svwb_ai.engine.cards.base import CardInstance


class GamePhase(Enum):
    MULLIGAN = auto()
    MAIN = auto()
    END = auto()


class CardType(Enum):
    FOLLOWER = auto()
    SPELL = auto()
    AMULET = auto()


class Keyword(Enum):
    """Card keywords/abilities"""
    SPELL_BOOST = auto()
    FANFARE = auto()
    LAST_WORD = auto()
    EVOLVE = auto()
    SUPER_EVOLVE = auto()
    WARD = auto()
    DRAIN = auto()
    VENGEANCE = auto()
    AMBUSH = auto()
    FLYING = auto()
    STORM = auto()
    RUSH = auto()
    ONSLAUGHT = auto()
    BARRIER = auto()


@dataclass
class BoardSlot:
    """Represents a slot on the board (follower or amulet)"""
    card: Optional['CardInstance'] = None

    def is_empty(self) -> bool:
        return self.card is None


@dataclass
class PlayerState:
    """Represents a single player's state"""
    leader_hp: int
    deck: list['CardInstance'] = field(default_factory=list)
    hand: list['CardInstance'] = field(default_factory=list)
    board: list[BoardSlot] = field(default_factory=lambda: [BoardSlot() for _ in range(5)])
    graveyard: list['CardInstance'] = field(default_factory=list)
    pp_current: int = 0
    pp_max: int = 0
    ep_remaining: int = 0
    sep_remaining: int = 0
    extra_pp_early_used: bool = False  # Whether ExPP used on turns 1-5
    extra_pp_late_used: bool = False   # Whether ExPP used on turns 6+
    is_first_player: bool = False

    def copy(self):
        """Create a deep copy of this player state"""
        from copy import deepcopy
        return deepcopy(self)


@dataclass
class GameState:
    """Represents the complete game state"""
    turn: int                    # Current turn (starts at 1)
    active_player_index: int     # 0 or 1
    players: tuple[PlayerState, PlayerState]
    phase: GamePhase = GamePhase.MULLIGAN
    winner: Optional[int] = None  # None = ongoing, 0 or 1 = winner

    def copy(self):
        """Create a deep copy of this game state"""
        from copy import deepcopy
        return deepcopy(self)

    @property
    def active_player(self) -> PlayerState:
        return self.players[self.active_player_index]

    @property
    def opponent_player(self) -> PlayerState:
        return self.players[1 - self.active_player_index]

    def get_player(self, index: int) -> PlayerState:
        return self.players[index]
