from svwb_ai.engine.action import Action, ActionType
from svwb_ai.engine.game_state import GameState, GamePhase
from svwb_ai.config.game_config import BOARD_MAX, HAND_MAX
from typing import List


def calc_effective_cost(card, player_state) -> int:
    """Calculate effective cost considering spell boost"""
    if card.card_type == 'SPELL':
        return max(0, card.cost - card.spell_boost_count)
    return card.cost


def can_play_card(state: GameState, player_idx: int, card_index: int) -> bool:
    """Check if a card can be played"""
    player = state.players[player_idx]
    opponent = state.players[1 - player_idx]

    if card_index < 0 or card_index >= len(player.hand):
        return False

    card = player.hand[card_index]
    cost = calc_effective_cost(card, player)

    # Check PP
    if player.pp_current < cost:
        return False

    # Check board space for followers and amulets
    if card.card_type in ['FOLLOWER', 'AMULET']:
        empty_slots = sum(1 for slot in player.board if slot.is_empty())
        if empty_slots == 0:
            return False

    return True


def can_attack(state: GameState, player_idx: int, attacker_index: int,
               target_is_leader: bool, target_index: int = -1) -> bool:
    """Check if a follower can attack"""
    player = state.players[player_idx]
    opponent = state.players[1 - player_idx]

    # Check attacker exists and is a follower
    if attacker_index < 0 or attacker_index >= len(player.board):
        return False

    attacker = player.board[attacker_index].card
    if attacker is None or attacker.card_type != 'FOLLOWER':
        return False

    # Can't attack if already exhausted this turn
    if attacker.exhausted:
        return False

    # Can't attack if summoning sick (unless has Rush/Ambush)
    if attacker.summoning_sick and 'RUSH' not in attacker.keywords and 'AMBUSH' not in attacker.keywords:
        return False

    # Can't attack if no attack power
    if attacker.attack <= 0:
        return False

    if target_is_leader:
        # Attacking leader is always valid if follower can act
        return True
    else:
        # Attacking follower/amulet
        if target_index < 0 or target_index >= len(opponent.board):
            return False
        target = opponent.board[target_index].card
        return target is not None


def can_evolve(state: GameState, player_idx: int, target_index: int) -> bool:
    """Check if a follower can evolve"""
    player = state.players[player_idx]

    if player.ep_remaining <= 0:
        return False

    if target_index < 0 or target_index >= len(player.board):
        return False

    follower = player.board[target_index].card
    if follower is None or follower.card_type != 'FOLLOWER':
        return False

    if follower.evolved or follower.super_evolved:
        return False

    # Check turn requirements
    turn = state.turn
    is_first = player.is_first_player
    if is_first and turn < 5:
        return False
    if not is_first and turn < 4:
        return False

    return True


def can_super_evolve(state: GameState, player_idx: int, target_index: int) -> bool:
    """Check if a follower can super evolve"""
    player = state.players[player_idx]

    if player.sep_remaining <= 0:
        return False

    if target_index < 0 or target_index >= len(player.board):
        return False

    follower = player.board[target_index].card
    if follower is None or follower.card_type != 'FOLLOWER':
        return False

    if follower.super_evolved:
        return False

    # Check turn requirements
    turn = state.turn
    is_first = player.is_first_player
    if is_first and turn < 7:
        return False
    if not is_first and turn < 6:
        return False

    return True


def can_use_extra_pp(state: GameState, player_idx: int) -> bool:
    """Check if extra PP can be used (second player only)"""
    player = state.players[player_idx]

    # Only second player can use ExPP
    if player.is_first_player:
        return False

    turn = state.turn

    # Turns 1-5: early ExPP
    if turn <= 5:
        return not player.extra_pp_early_used
    # Turns 6+: late ExPP
    else:
        return not player.extra_pp_late_used


def get_legal_actions(state: GameState) -> List[Action]:
    """Generate all legal actions for current player"""
    actions = []
    player_idx = state.active_player_index
    player = state.players[player_idx]

    if state.phase == GamePhase.MAIN:
        # Play cards from hand
        for i in range(len(player.hand)):
            if can_play_card(state, player_idx, i):
                actions.append(Action(ActionType.PLAY_CARD, card_index=i))
                # TODO: Add PLAY_CARD_ENHANCE for cards with enhancement

        # Attack with followers
        for attacker_idx in range(len(player.board)):
            attacker = player.board[attacker_idx].card
            if attacker is None or attacker.card_type != 'FOLLOWER':
                continue

            # Attack leader
            if can_attack(state, player_idx, attacker_idx, target_is_leader=True):
                actions.append(Action(
                    ActionType.ATTACK,
                    attacker_index=attacker_idx,
                    target_is_leader=True
                ))

            # Attack opponent's board
            opponent = state.players[1 - player_idx]
            for target_idx in range(len(opponent.board)):
                if opponent.board[target_idx].card is not None:
                    if can_attack(state, player_idx, attacker_idx, target_is_leader=False,
                                target_index=target_idx):
                        actions.append(Action(
                            ActionType.ATTACK,
                            attacker_index=attacker_idx,
                            target_index=target_idx,
                            target_is_leader=False
                        ))

        # Evolve followers
        for target_idx in range(len(player.board)):
            if can_evolve(state, player_idx, target_idx):
                actions.append(Action(ActionType.EVOLVE, target_index=target_idx))

        # Super evolve followers
        for target_idx in range(len(player.board)):
            if can_super_evolve(state, player_idx, target_idx):
                actions.append(Action(ActionType.SUPER_EVOLVE, target_index=target_idx))

        # Use extra PP (second player only)
        if can_use_extra_pp(state, player_idx):
            actions.append(Action(ActionType.USE_EXTRA_PP))

        # TODO: Amulet activation

    # End turn is always legal
    actions.append(Action(ActionType.END_TURN))

    return actions
