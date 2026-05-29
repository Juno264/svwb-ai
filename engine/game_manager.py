import random
from svwb_ai.engine.game_state import GameState, GamePhase, PlayerState, CardType
from svwb_ai.engine.action import Action, ActionType
from svwb_ai.engine.legal_actions import get_legal_actions
from svwb_ai.engine.effect_engine import EffectEngine
from svwb_ai.engine.cards.base import CardInstance
from svwb_ai.config.game_config import (
    LEADER_HP, PP_MAX, INITIAL_HAND_SIZE, EP_COUNT, SEP_COUNT
)
from typing import List, Tuple, Optional, Callable


class GameManager:
    """Manages a game of Shadowverse"""

    def __init__(self, deck1: List[CardInstance], deck2: List[CardInstance],
                 agent1: Callable = None, agent2: Callable = None):
        """
        Initialize game.

        Args:
            deck1: First player's deck
            deck2: Second player's deck
            agent1: Function to get action for player 1
            agent2: Function to get action for player 2
        """
        self.effect_engine = EffectEngine()
        self.agents = [agent1, agent2]

        # Initialize players
        self.state = self._init_game(deck1, deck2)

    def _init_game(self, deck1: List[CardInstance], deck2: List[CardInstance]) -> GameState:
        """Initialize game state"""
        # Shuffle decks
        deck1_shuffled = deck1.copy()
        deck2_shuffled = deck2.copy()
        random.shuffle(deck1_shuffled)
        random.shuffle(deck2_shuffled)

        # Create player states
        player1 = PlayerState(
            leader_hp=LEADER_HP,
            deck=deck1_shuffled,
            hand=[],
            is_first_player=True
        )

        player2 = PlayerState(
            leader_hp=LEADER_HP,
            deck=deck2_shuffled,
            hand=[],
            is_first_player=False
        )

        # Create game state
        state = GameState(
            turn=0,
            active_player_index=0,
            players=(player1, player2),
            phase=GamePhase.MULLIGAN
        )

        # Draw initial hands
        state = self._draw_initial_hands(state)

        return state

    def _draw_initial_hands(self, state: GameState) -> GameState:
        """Draw initial hands for both players"""
        for player_idx in [0, 1]:
            player = state.players[player_idx]
            for _ in range(INITIAL_HAND_SIZE):
                if player.deck:
                    card = player.deck.pop(0)
                    player.hand.append(card)
        return state

    def start_turn(self, player_idx: int) -> GameState:
        """Start a new turn for a player"""
        state = self.state.copy()
        player = state.players[player_idx]
        state.active_player_index = player_idx
        state.phase = GamePhase.MAIN

        # Increment turn counter (only on first player's turn)
        if player_idx == 0:
            state.turn += 1

        # Clear summoning sickness and exhausted for all followers on board
        for board_slot in player.board:
            if board_slot.card and board_slot.card.card_type == 'FOLLOWER':
                board_slot.card.summoning_sick = False
                board_slot.card.exhausted = False

        # Reset/refill resources
        player.pp_current = min(player.pp_max + 1, PP_MAX)
        player.pp_max = min(player.pp_max + 1, PP_MAX)

        # Recover EP and SEP
        if player.is_first_player:
            ep_recover_turn = 5
            sep_recover_turn = 7
        else:
            ep_recover_turn = 4
            sep_recover_turn = 6

        if state.turn >= ep_recover_turn:
            player.ep_remaining = min(player.ep_remaining + 1, EP_COUNT)

        if state.turn >= sep_recover_turn:
            player.sep_remaining = min(player.sep_remaining + 1, SEP_COUNT)

        # Process turn start effects
        state = self.effect_engine.process_turn_start(state, player_idx)

        # Draw a card
        if player.deck:
            drawn = player.deck.pop(0)
            if len(player.hand) < 9:  # Max hand size
                player.hand.append(drawn)
            else:
                # Card is destroyed if hand is full
                player.graveyard.append(drawn)

        self.state = state
        return state

    def execute_action(self, action: Action) -> GameState:
        """Execute an action and update game state"""
        state = self.state.copy()
        player_idx = state.active_player_index
        player = state.players[player_idx]

        if action.action_type == ActionType.PLAY_CARD:
            if action.card_index < 0 or action.card_index >= len(player.hand):
                return state

            card = player.hand[action.card_index]
            cost = max(0, card.cost - card.spell_boost_count) if card.card_type == CardType.SPELL else card.cost

            if player.pp_current < cost:
                return state

            # Spell cards go to graveyard, others to board
            if card.card_type == 'SPELL':
                player.graveyard.append(card)
                player.hand.pop(action.card_index)
                # Spells have fanfare effects
                state = self.effect_engine.process_fanfare(state, player_idx, card, -1, [])
            else:
                # Find empty board slot
                board_index = -1
                for i, slot in enumerate(player.board):
                    if slot.is_empty():
                        board_index = i
                        break

                if board_index >= 0:
                    player.hand.pop(action.card_index)
                    card_copy = card.copy()
                    card_copy.summoning_sick = True
                    player.board[board_index].card = card_copy
                    state = self.effect_engine.process_fanfare(state, player_idx, card_copy, board_index, [])

            player.pp_current -= cost

        elif action.action_type == ActionType.ATTACK:
            state = self.effect_engine.process_attack(
                state,
                action.attacker_index,
                action.target_is_leader,
                action.target_index
            )
            state = self.effect_engine.process_death_check(state)

        elif action.action_type == ActionType.EVOLVE:
            if action.target_index >= 0 and action.target_index < len(player.board):
                follower = player.board[action.target_index].card
                if follower and not follower.evolved:
                    state = self.effect_engine.process_evolve(state, player_idx, follower, action.target_index)

        elif action.action_type == ActionType.SUPER_EVOLVE:
            if action.target_index >= 0 and action.target_index < len(player.board):
                follower = player.board[action.target_index].card
                if follower and not follower.super_evolved:
                    state = self.effect_engine.process_super_evolve(state, player_idx, follower, action.target_index)

        elif action.action_type == ActionType.USE_EXTRA_PP:
            if not player.is_first_player:
                if state.turn <= 5 and not player.extra_pp_early_used:
                    player.pp_max += 1
                    player.pp_current += 1
                    player.extra_pp_early_used = True
                elif state.turn > 5 and not player.extra_pp_late_used:
                    player.pp_current += 1
                    player.extra_pp_late_used = True

        elif action.action_type == ActionType.END_TURN:
            # Process turn end effects
            state = self.effect_engine.process_turn_end(state, player_idx)
            # Check win condition
            state = self.effect_engine.check_win_condition(state)
            state.phase = GamePhase.END

        self.state = state
        return state

    def play_turn(self) -> bool:
        """Play one turn. Returns True if game continues, False if game ends"""
        player_idx = self.state.active_player_index

        # Start turn
        self.start_turn(player_idx)

        # Get actions from agent
        agent = self.agents[player_idx]
        if agent is None:
            # Default to end turn if no agent
            self.execute_action(Action(ActionType.END_TURN))
        else:
            # Let agent play
            while self.state.phase == GamePhase.MAIN:
                legal_actions = get_legal_actions(self.state)
                action = agent(self.state, legal_actions)
                self.execute_action(action)

        # Check if game is over
        if self.state.winner is not None:
            return False

        # Switch to other player
        state = self.state.copy()
        state.active_player_index = 1 - state.active_player_index
        self.state = state

        return True

    def play_game(self) -> int:
        """Play full game. Returns winner (0 or 1)"""
        self._in_game = True
        max_turns = 500  # Safety limit (2 players alternating)

        for _ in range(max_turns):
            if not self.play_turn():
                return self.state.winner

        # Game did not finish - return None or raise
        return None
