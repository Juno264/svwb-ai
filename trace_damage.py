#!/usr/bin/env python
"""Trace damage dealt in a game"""

from svwb_ai.engine.game_manager import GameManager
from svwb_ai.engine.cards.base import CardInstance
from svwb_ai.engine.legal_actions import get_legal_actions
from svwb_ai.engine.action import ActionType
from svwb_ai.ai.rule_agent import RuleAgent


def create_test_deck():
    """Create a simple test deck"""
    deck = []
    for _ in range(40):
        card = CardInstance(
            card_id="follower",
            name="Follower 2/2",
            cost=2,
            card_type='FOLLOWER'
        )
        card.attack = 2
        card.hp = 2
        deck.append(card)
    return deck


if __name__ == "__main__":
    print("Starting damage trace...")
    deck1 = create_test_deck()
    deck2 = create_test_deck()

    agent1 = RuleAgent()
    agent2 = RuleAgent()

    manager = GameManager(deck1, deck2, agent1.get_action, agent2.get_action)

    # Play game and trace damage
    for turn_num in range(15):
        player_idx = manager.state.active_player_index
        opponent_idx = 1 - player_idx
        p0_hp_before = manager.state.players[0].leader_hp
        p1_hp_before = manager.state.players[1].leader_hp

        manager.start_turn(player_idx)

        # Play actions
        while manager.state.phase.name == 'MAIN':
            legal_actions = get_legal_actions(manager.state)
            agent_func = agent1.get_action if player_idx == 0 else agent2.get_action
            action = agent_func(manager.state, legal_actions)

            if action.action_type == ActionType.ATTACK:
                attacker = manager.state.players[player_idx].board[action.attacker_index].card
                print(f"Turn {turn_num+1}: Player {player_idx} attacks with {attacker.name} (ATK={attacker.attack})")

            manager.execute_action(action)

            if action.action_type == ActionType.END_TURN:
                break

        # Check HP after turn
        p0_hp_after = manager.state.players[0].leader_hp
        p1_hp_after = manager.state.players[1].leader_hp

        if p0_hp_before != p0_hp_after or p1_hp_before != p1_hp_after:
            print(f"  P0: {p0_hp_before} -> {p0_hp_after}, P1: {p1_hp_before} -> {p1_hp_after}")

        if manager.state.winner is not None:
            print(f"Game ended! Winner: {manager.state.winner}")
            break

        # Switch to next player
        manager.state.active_player_index = 1 - manager.state.active_player_index
