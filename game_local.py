import random

# Constants
SUITS = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
BID_SUITS = ['C', 'D', 'H', 'S', 'NT']  # Club, Diamond, Heart, Spade, No Trump


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()


class Player:
    def __init__(self, name):
        self.name = name
        self.hand = []

    def receive_card(self, card):
        self.hand.append(card)

    def show_hand(self):
        return ', '.join(map(str, self.hand))


class Bidding:
    def __init__(self):
        self.bids = []
        self.passes = 0
        self.current_highest_bid = None

    def place_bid(self, player, bid):
        self.bids.append((player.name, bid))
        self.passes = 0
        self.current_highest_bid = bid

    def pass_bid(self, player):
        self.bids.append((player.name, "Pass"))
        self.passes += 1

    def is_bidding_over(self):
        return self.passes >= 3

    def is_valid_bid(self, bid):
        if self.current_highest_bid is None:
            return True
        bid_value = self.convert_bid_to_value(bid)
        current_highest_bid_value = self.convert_bid_to_value(self.current_highest_bid)
        return bid_value > current_highest_bid_value

    @staticmethod
    def convert_bid_to_value(bid):
        bid_rank, bid_suit = bid[:-1], bid[-1]
        bid_suit_value = BID_SUITS.index(bid_suit)
        return int(bid_rank) * 10 + bid_suit_value

    def print_bidding_history(self):
        return '\n'.join([f"{player}: {bid}" for player, bid in self.bids])


class GameLogic:
    def __init__(self):
        self.deck = Deck()
        self.players = [Player(f"Player {i + 1}") for i in range(4)]
        self.bidding = Bidding()
        self.current_player_index = 0

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
            return
        if bid.lower() == "pass":
            self.bidding.pass_bid(player)
        elif self.bidding.is_valid_bid(bid):
            self.bidding.place_bid(player, bid)
        else:
            print("Invalid bid. You must bid higher than the current highest bid.")
            return False
        return True


def main():
    game = GameLogic()
    game.start_game()

    print("Starting the game of Bridge!")

    # Display hands
    for player in game.players:
        print(f"{player.name} hand: {player.show_hand()}")

    # Bidding phase
    print("\nBidding Phase:")
    while not game.bidding.is_bidding_over():
        current_player = game.get_current_player()
        print(f"{current_player.name}'s turn to bid.")
        bid = input("Enter your bid (e.g., '1C', '2D', 'Pass'): ").strip().upper()
        if game.bid(current_player, bid):
            game.next_turn()

    print("Bidding phase is over.")
    print("Bidding history:\n", game.bidding.print_bidding_history())


if __name__ == "__main__":
    main()