from .deck import Deck
from .player import Player

class GameState:
    def __init__(self):
        self.deck = Deck()
        self.players = [Player(f"Player {i + 1}") for i in range(4)]
        self.current_turn = 0

    def deal_cards(self):
        for _ in range(13):
            for player in self.players:
                player.receive_card(self.deck.deal())

    def next_turn(self):
        self.current_turn = (self.current_turn + 1) % 4

    def get_current_player(self):
        return self.players[self.current_turn]