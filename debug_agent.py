#!/usr/bin/env python
"""Debug script to trace agent decisions"""

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


class DebuggingRuleAgent(RuleAgent):
    """Rule agent that prints debug info"""

    def get_action(self, state, legal_actions):
        """Get action with debug output"""
        action = super().get_action(state, legal_actions)

        # Count action types
        action_counts = {}
        for a in legal_actions:
            action_type = str(a.action_type)
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        print(f"  Legal actions: {action_counts} => chose {action.action_type}")
        return action


if __name__ == "__main__":
    print("Starting debug game...")
    deck1 = create_test_deck()
    deck2 = create_test_deck()

    agent1 = DebuggingRuleAgent()
    agent2 = DebuggingRuleAgent()

    manager = GameManager(deck1, deck2, agent1.get_action, agent2.get_action)

    # Play game with debug output
    max_turns = 30
    for turn_num in range(max_turns):
        print(f"\n=== Turn {turn_num + 1} ===")
        player_idx = manager.state.active_player_index
        player = manager.state.active_player

        print(f"Player {player_idx}: HP={player.leader_hp}, PP={player.pp_current}/{player.pp_max}, Hand={len(player.hand)}, Board={len([s for s in player.board if s.card])}")

        manager.start_turn(player_idx)

        # Play until phase changes
        action_count = 0
        while manager.state.phase.name == 'MAIN':
            legal_actions = get_legal_actions(manager.state)
            if not legal_actions:
                print("  ERROR: No legal actions in MAIN phase!")
                break

            agent_func = agent1.get_action if player_idx == 0 else agent2.get_action
            action = agent_func(manager.state, legal_actions)
            manager.execute_action(action)
            action_count += 1

            if action_count > 20:
                print(f"  WARNING: Too many actions in one turn!")
                break

        # Check game status
        if manager.state.winner is not None:
            print(f"Game ended! Winner: {manager.state.winner}")
            break

        # Switch to next player
        manager.state.active_player_index = 1 - manager.state.active_player_index
