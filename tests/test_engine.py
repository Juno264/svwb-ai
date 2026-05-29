"""Tests for game engine functionality"""

import pytest
from svwb_ai.engine.game_state import GameState, PlayerState, GamePhase, CardType
from svwb_ai.engine.game_manager import GameManager
from svwb_ai.engine.action import Action, ActionType
from svwb_ai.engine.legal_actions import get_legal_actions
from svwb_ai.engine.cards.base import CardInstance
from svwb_ai.ai.random_agent import RandomAgent


def create_test_deck():
    """Create a test deck"""
    deck = []
    for _ in range(40):
        card = CardInstance(
            card_id="test_card",
            name="Test Card",
            cost=1,
            card_type="FOLLOWER"
        )
        card.attack = 1
        card.hp = 1
        deck.append(card)
    return deck


def test_game_initialization():
    """Test that game initializes correctly"""
    deck1 = create_test_deck()
    deck2 = create_test_deck()
    manager = GameManager(deck1, deck2)

    assert manager.state.turn == 0
    assert manager.state.active_player_index == 0
    assert manager.state.phase == GamePhase.MULLIGAN
    assert len(manager.state.players[0].hand) == 4
    assert len(manager.state.players[1].hand) == 4


def test_legal_actions_generated():
    """Test that legal actions are generated correctly"""
    deck1 = create_test_deck()
    deck2 = create_test_deck()
    manager = GameManager(deck1, deck2)

    # Start a turn
    manager.start_turn(0)

    actions = get_legal_actions(manager.state)
    assert len(actions) > 0
    # Should have at least END_TURN
    assert any(a.action_type == ActionType.END_TURN for a in actions)


def test_card_play():
    """Test playing a card"""
    deck1 = create_test_deck()
    deck2 = create_test_deck()
    manager = GameManager(deck1, deck2)
    manager.start_turn(0)

    initial_hand_size = len(manager.state.active_player.hand)
    initial_pp = manager.state.active_player.pp_current

    # Play a card
    card_action = next(
        (a for a in get_legal_actions(manager.state) if a.action_type == ActionType.PLAY_CARD),
        None
    )

    if card_action:
        manager.execute_action(card_action)
        # Hand size should decrease
        assert len(manager.state.active_player.hand) == initial_hand_size - 1


def test_pp_management():
    """Test PP (Play Points) management"""
    deck1 = create_test_deck()
    deck2 = create_test_deck()
    manager = GameManager(deck1, deck2)

    initial_pp = 0
    for _ in range(3):
        manager.start_turn(0)
        turn_pp = manager.state.players[0].pp_max
        assert turn_pp > initial_pp or turn_pp == 10  # Should increase or cap at 10
        initial_pp = turn_pp


def test_attack_resolution():
    """Test that attacks work"""
    deck1 = create_test_deck()
    deck2 = create_test_deck()
    manager = GameManager(deck1, deck2)
    manager.start_turn(0)

    # Manually place a follower on board
    player = manager.state.players[0]
    card = CardInstance("test", "Test", 1, CardType.FOLLOWER)
    card.attack = 5
    card.hp = 5
    card.summoning_sick = False
    player.board[0].card = card

    initial_opponent_hp = manager.state.players[1].leader_hp

    # Attack opponent leader
    attack_action = Action(
        ActionType.ATTACK,
        attacker_index=0,
        target_is_leader=True
    )
    manager.execute_action(attack_action)

    # Opponent should take damage
    assert manager.state.players[1].leader_hp == initial_opponent_hp - 5


def test_win_condition():
    """Test win condition detection"""
    deck1 = create_test_deck()
    deck2 = create_test_deck()
    manager = GameManager(deck1, deck2)

    # Set opponent HP to 1
    manager.state.players[1].leader_hp = 1

    # Play attack that kills
    player = manager.state.players[0]
    card = CardInstance("test", "Test", 1, CardType.FOLLOWER)
    card.attack = 5
    card.hp = 5
    card.summoning_sick = False
    player.board[0].card = card

    attack_action = Action(ActionType.ATTACK, attacker_index=0, target_is_leader=True)
    manager.execute_action(attack_action)

    # End turn to trigger win condition check
    manager.execute_action(Action(ActionType.END_TURN))

    # Game should be over
    assert manager.state.winner == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
