from svwb_ai.engine.game_state import GameState
from typing import List


def apply_mulligan(state: GameState, player_idx: int, keep_indices: List[int]) -> GameState:
    """
    Apply mulligan for a player.

    Args:
        state: Current game state
        player_idx: 0 or 1 (which player is mulliganing)
        keep_indices: List of hand card indices to keep (0-based)

    Returns:
        Updated game state with mulligan applied
    """
    state = state.copy()
    player = state.players[player_idx]

    # Determine which cards to mulligan (cards not in keep_indices)
    cards_to_mulligan = []
    for i in range(len(player.hand)):
        if i not in keep_indices:
            cards_to_mulligan.append(player.hand[i])

    # Return mulligan cards to deck
    player.deck.extend(cards_to_mulligan)

    # Remove mulligan cards from hand
    new_hand = []
    for i in range(len(player.hand)):
        if i in keep_indices:
            new_hand.append(player.hand[i])
    player.hand = new_hand

    # Draw replacement cards
    for _ in range(len(cards_to_mulligan)):
        if player.deck:
            drawn = player.deck.pop(0)
            player.hand.append(drawn)

    return state
