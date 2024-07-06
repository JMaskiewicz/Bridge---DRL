from .game_state import GameState

class Bidding:
    def __init__(self):
        self.bids = []
        self.passes = 0

    def place_bid(self, player, bid):
        self.bids.append((player, bid))
        self.passes = 0

    def pass_bid(self):
        self.passes += 1

    def is_bidding_over(self):
        return self.passes >= 3

    def print_bidding_history(self):
        return '\n'.join([f"{player}: {bid}" for player, bid in self.bids])


class PlayPhase:
    def __init__(self):
        self.tricks = []

    def play_card(self, player, card):
        self.tricks.append((player, card))

class GameLogic:
    def __init__(self):
        self.game_state = GameState()
        self.bidding = Bidding()
        self.play_phase = PlayPhase()

    def start_game(self):
        self.game_state.deal_cards()

    def bid(self, player, bid):
        if self.bidding.is_bidding_over():
            print("Bidding phase is over.")
            return
        if bid:
            self.bidding.place_bid(player, bid)
        else:
            self.bidding.pass_bid()

    def play_card(self, player, card):
        self.play_phase.play_card(player, card)
        self.game_state.next_turn()

    def print_current_player_hand(self):
        current_player = self.game_state.get_current_player()
        return current_player.show_hand()

    def print_bidding_history(self):
        return self.bidding.print_bidding_history()