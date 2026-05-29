from svwb_ai.engine.game_state import GameState, CardType
from typing import List, Optional, Dict, Callable, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from svwb_ai.engine.cards.base import CardInstance


class EffectEngine:
    """Handles all game effects and state transitions"""

    def __init__(self):
        self.card_effects: Dict[str, Callable] = {}

    def register_card_effect(self, card_id: str, effect_func: Callable):
        """Register a custom effect function for a card"""
        self.card_effects[card_id] = effect_func

    def process_fanfare(self, state: GameState, player_idx: int, card: Any,
                       board_index: int, targets: List[int] = None) -> GameState:
        """
        Process fanfare effect when card is played.
        This is called after the card is placed on board/in graveyard.
        """
        if targets is None:
            targets = []

        # Check if card has custom effect
        if card.card_id in self.card_effects:
            state = self.card_effects[card.card_id](state, player_idx, card, 'fanfare', targets)

        return state

    def process_last_word(self, state: GameState, player_idx: int, card: Any) -> GameState:
        """Process last word effect when follower is destroyed"""
        if card.card_id in self.card_effects:
            state = self.card_effects[card.card_id](state, player_idx, card, 'last_word', [])

        return state

    def process_evolve(self, state: GameState, player_idx: int, follower: Any,
                      board_index: int) -> GameState:
        """Process evolution effect"""
        if follower.evolved or follower.super_evolved:
            return state

        follower = state.players[player_idx].board[board_index].card

        # Mark as evolved
        follower.evolved = True

        # Consume EP
        state.players[player_idx].ep_remaining -= 1

        # Trigger evolution effect
        if follower.card_id in self.card_effects:
            state = self.card_effects[follower.card_id](state, player_idx, follower, 'evolve', [])

        return state

    def process_super_evolve(self, state: GameState, player_idx: int, follower: Any,
                            board_index: int) -> GameState:
        """Process super evolution effect (includes evolve effects)"""
        if follower.super_evolved:
            return state

        follower = state.players[player_idx].board[board_index].card

        # Mark as super evolved
        follower.super_evolved = True
        follower.evolved = True

        # Consume SEP
        state.players[player_idx].sep_remaining -= 1

        # Trigger super evolve effect
        if follower.card_id in self.card_effects:
            state = self.card_effects[follower.card_id](state, player_idx, follower, 'super_evolve', [])

        return state

    def process_attack(self, state: GameState, attacker_idx: int, target_is_leader: bool,
                      target_idx: Optional[int] = None) -> GameState:
        """
        Process attack resolution.
        Attacker is from active player, target is opponent.
        """
        player_idx = state.active_player_index
        opponent_idx = 1 - player_idx
        player = state.players[player_idx]
        opponent = state.players[opponent_idx]

        attacker = player.board[attacker_idx].card
        if attacker is None or attacker.card_type != CardType.FOLLOWER:
            return state

        # Mark as exhausted and remove summoning sick
        attacker.exhausted = True
        attacker.summoning_sick = False

        if target_is_leader:
            # Deal damage to leader
            damage = attacker.attack
            opponent.leader_hp -= damage
        else:
            # Attack follower/amulet
            target = opponent.board[target_idx].card
            if target is None:
                return state

            if target.card_type == CardType.FOLLOWER:
                # Follower vs follower combat
                attacker.hp -= target.attack
                target.hp -= attacker.attack
            elif target.card_type == CardType.AMULET:
                # Attacking amulet
                target.hp -= attacker.attack
                # Amulets have 1 HP by default, destroyed immediately
                if target.hp <= 0:
                    opponent.board[target_idx].card = None

        return state

    def process_turn_start(self, state: GameState, player_idx: int) -> GameState:
        """Process turn start effects (amulet countdown, etc.)"""
        player = state.players[player_idx]

        # Process amulet turn start effects
        for board_slot in player.board:
            if board_slot.card and board_slot.card.card_type == CardType.AMULET:
                card = board_slot.card
                if card.card_id in self.card_effects:
                    state = self.card_effects[card.card_id](state, player_idx, card, 'turn_start', [])

        return state

    def process_turn_end(self, state: GameState, player_idx: int) -> GameState:
        """Process turn end effects (amulet countdown activation, etc.)"""
        player = state.players[player_idx]

        # Process amulet countdowns and turn end effects
        for i, board_slot in enumerate(player.board):
            if board_slot.card and board_slot.card.card_type == CardType.AMULET:
                card = board_slot.card
                # Decrement countdown
                if card.countdown is not None and card.countdown > 0:
                    card.countdown -= 1
                    # Activate if countdown reached 0
                    if card.countdown == 0:
                        if card.card_id in self.card_effects:
                            state = self.card_effects[card.card_id](state, player_idx, card, 'activate', [])
                # Turn end effect
                if card.card_id in self.card_effects:
                    state = self.card_effects[card.card_id](state, player_idx, card, 'turn_end', [])

        return state

    def process_death_check(self, state: GameState) -> GameState:
        """
        Check for dead followers and trigger last word effects.
        Must be called after damage is dealt.
        """
        # Check both players' boards
        for player_idx in [0, 1]:
            player = state.players[player_idx]
            dead_indices = []

            for i, board_slot in enumerate(player.board):
                if board_slot.card and board_slot.card.card_type == CardType.FOLLOWER:
                    if board_slot.card.hp <= 0:
                        dead_indices.append(i)

            # Process last word effects and remove dead followers
            for i in reversed(dead_indices):  # Process in reverse to avoid index issues
                card = player.board[i].card
                state = self.process_last_word(state, player_idx, card)
                # Move to graveyard
                player.graveyard.append(card)
                player.board[i].card = None

        return state

    def check_win_condition(self, state: GameState) -> GameState:
        """Check if game is over (leader HP <= 0)"""
        if state.players[0].leader_hp <= 0:
            state.winner = 1
        elif state.players[1].leader_hp <= 0:
            state.winner = 0

        return state
