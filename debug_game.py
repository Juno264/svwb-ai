#!/usr/bin/env python
"""Debug script to understand game flow"""

from svwb_ai.engine.game_manager import GameManager
from svwb_ai.engine.cards.base import CardInstance
from svwb_ai.engine.game_state import CardType
from svwb_ai.engine.legal_actions import get_legal_actions
from svwb_ai.ai.rule_agent import RuleAgent


def create_test_deck():
    """Create a test deck"""
    deck = []
    for _ in range(40):
        card = CardInstance(
            card_id="test_card",
            name="Test Card",
            cost=1,
            card_type='FOLLOWER'
        )
        card.attack = 1
        card.hp = 1
        deck.append(card)
    return deck


if __name__ == "__main__":
    print("Starting debug game...")
    deck1 = create_test_deck()
    deck2 = create_test_deck()

    agent1 = RuleAgent()
    agent2 = RuleAgent()

    manager = GameManager(deck1, deck2, agent1.get_action, agent2.get_action)

    # Play first few turns manually
    for turn_num in range(5):
        print(f"\n=== Turn {turn_num + 1} ===")
        player_idx = manager.state.active_player_index
        player = manager.state.active_player
        opponent = manager.state.opponent_player

        print(f"Active player: {player_idx}")
        print(f"Phase: {manager.state.phase}")
        print(f"Player {player_idx} HP: {player.leader_hp}, PP: {player.pp_current}/{player.pp_max}")
        print(f"Opponent HP: {opponent.leader_hp}")
        print(f"Hand size: {len(player.hand)}")
        board_state = [slot.card.name if slot.card else "empty" for slot in player.board]
        print(f"Board: {board_state}")

        manager.start_turn(player_idx)

        print(f"\nAfter start_turn:")
        print(f"Phase: {manager.state.phase}")
        print(f"Hand size: {len(player.hand)}")

        # Get legal actions
        legal_actions = get_legal_actions(manager.state)
        print(f"Legal actions count: {len(legal_actions)}")
        print(f"Action types: {[a.action_type for a in legal_actions[:3]]}")

        # Get agent action and execute
        if agent1 if player_idx == 0 else agent2:
            agent_func = agent1.get_action if player_idx == 0 else agent2.get_action
            action = agent_func(manager.state, legal_actions)
            print(f"Agent chose: {action.action_type}")
            manager.execute_action(action)

        # Check phase after executing turn
        print(f"After execute_action: phase = {manager.state.phase}, winner = {manager.state.winner}")

        # Switch to next player
        if manager.state.winner is None:
            manager.state.active_player_index = 1 - manager.state.active_player_index
