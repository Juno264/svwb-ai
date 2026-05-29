#!/usr/bin/env python
"""Demo script to run a single game"""

from svwb_ai.engine.game_manager import GameManager
from svwb_ai.engine.cards.base import CardInstance
from svwb_ai.engine.game_state import CardType
from svwb_ai.ai.rule_agent import RuleAgent


def create_demo_deck():
    """Create a demo deck"""
    deck = []
    for _ in range(40):
        card = CardInstance(
            card_id="follower",
            name="Demo Follower",
            cost=2,
            card_type='FOLLOWER'
        )
        card.attack = 1
        card.hp = 1
        deck.append(card)
    return deck


if __name__ == "__main__":
    print("Running demo game...")
    deck1 = create_demo_deck()
    deck2 = create_demo_deck()

    agent1 = RuleAgent()
    agent2 = RuleAgent()

    manager = GameManager(deck1, deck2, agent1.get_action, agent2.get_action)

    try:
        winner = manager.play_game()
        print(f"Game finished!")
        print(f"Winner: Player {winner}")
        print(f"Final turn: {manager.state.turn}")
        print(f"Player 1 HP: {manager.state.players[0].leader_hp}")
        print(f"Player 2 HP: {manager.state.players[1].leader_hp}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
