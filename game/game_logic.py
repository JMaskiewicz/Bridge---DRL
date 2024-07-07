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
        self.deck = Deck()
        self.players = [Player(f"Player {i + 1}") for i in range(4)]
        self.bidding = Bidding()
        self.current_player_index = 0
        self.tricks = []
        self.trump_suit = None
        self.declarer = None
        self.tricks_won = {1: 0, 2: 0}  # Tracks tricks won by each team

    def start_game(self):
        self.deal_cards()

    def deal_cards(self):
        for _ in range(13):
            for player in self.players:
                player.receive_card(self.deck.deal())

    def get_current_player(self):
        return self.players[self.current_player_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + 1) % 4

    def bid(self, player, bid):
        if self.bidding.is_bidding_over():
            print("Bidding phase is over.")
            return False
        if bid.lower() == "pass":
            self.bidding.pass_bid(player)
        elif self.bidding.is_valid_bid(bid):
            self.bidding.place_bid(player, bid)
        else:
            print("Invalid bid. You must bid higher than the current highest bid and within the valid bid range.")
            return False
        return True

    def play_card(self, player, card_str):
        card_obj = next((c for c in player.hand if str(c) == card_str), None)
        if not card_obj:
            print("Invalid card. Try again.")
            return False

        # Check if the player follows the lead suit if possible
        if self.tricks and self.tricks[-1].cards:
            leading_suit = self.tricks[-1].cards[0][1].suit
            if any(c.suit == leading_suit for c in player.hand) and card_obj.suit != leading_suit:
                print(f"You must follow suit with {leading_suit} if you have one.")
                return False

        self.tricks[-1].play_card(player, player.play_card(card_obj))
        return True

    def set_trump_and_declarer(self):
        if self.bidding.current_highest_bid:
            bid_suit = self.bidding.current_highest_bid[-1]
            self.trump_suit = None if bid_suit == 'NT' else bid_suit
            self.declarer = self.bidding.declarer

    def set_current_player_to_next_of_declarer(self):
        for i, player in enumerate(self.players):
            if player == self.bidding.declarer:
                self.current_player_index = (i + 1) % 4
                break

    def set_current_player_to_winner(self, winner):
        for i, player in enumerate(self.players):
            if player == winner:
                self.current_player_index = i
                break
