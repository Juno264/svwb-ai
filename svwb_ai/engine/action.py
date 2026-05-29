from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional


class ActionType(Enum):
    PLAY_CARD = auto()          # Play card normally
    PLAY_CARD_ENHANCE = auto()  # Play card with enhancement
    ATTACK = auto()             # Follower attacks
    EVOLVE = auto()             # Evolution (costs EP)
    SUPER_EVOLVE = auto()       # Super evolution (costs SEP)
    USE_EXTRA_PP = auto()       # Use extra PP (second player only)
    ACTIVATE_AMULET = auto()    # Activate amulet ability
    END_TURN = auto()           # End turn


@dataclass(frozen=True)
class Action:
    action_type: ActionType
    card_index: Optional[int] = None      # Hand card index (for PLAY_* actions)
    attacker_index: Optional[int] = None  # Board index of attacker
    target_index: Optional[int] = None    # Target board index or hand/graveyard index
    target_is_leader: bool = False        # Whether target is opponent's leader
