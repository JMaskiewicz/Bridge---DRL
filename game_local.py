import random


'''
quarterback - one player that won bidding and will play the hand
partner - the player sitting opposite the quarterback
defenders 1 - the other who will play against the quarterback and have Whist lead
defenders 2 - the other who will play against the quarterback and have second lead
'''

# Constants
SUITS = ['C', 'D', 'H', 'S']  # Clubs, Diamonds, Hearts, Spades
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
BID_SUITS = ['C', 'D', 'H', 'S', 'NT']  # Club, Diamond, Heart, Spade, No Trump
VALID_BIDS = [f"{rank}{suit}" for rank in range(1, 8) for suit in BID_SUITS]



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

    def play_card(self, card):
        self.hand.remove(card)
        return card

    def show_hand(self):
        return ', '.join(map(str, self.hand))


class Bidding:
    def __init__(self):
        self.bids = []
        self.passes = 0
        self.current_highest_bid = None
        self.declarer = None

    def place_bid(self, player, bid):
        self.bids.append((player.name, bid))
        self.passes = 0
        self.current_highest_bid = bid
        self.declarer = player

    def pass_bid(self, player):
        self.bids.append((player.name, "Pass"))
        self.passes += 1

    def is_bidding_over(self):
        return len(self.bids) >= 4 and self.passes >= 3

    def is_four_consecutive_passes(self):
        if len(self.bids) < 4:
            return False
        return all(bid == "Pass" for _, bid in self.bids[-4:])

    def is_valid_bid(self, bid):
        if bid not in VALID_BIDS:
            return False
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


class Trick:
    def __init__(self):
        self.cards = []

    def play_card(self, player, card):
        self.cards.append((player, card))

    def determine_winner(self):
        # Assuming the first card determines the suit to follow
        leading_suit = self.cards[0][1].suit
        winning_card = self.cards[0]
        for player, card in self.cards:
            if card.suit == leading_suit and RANKS.index(card.rank) > RANKS.index(winning_card[1].rank):
                winning_card = (player, card)
        return winning_card[0]


class GameLogic:
    def __init__(self):
        self.deck = Deck()
        self.players = [Player(f"Player {i + 1}") for i in range(4)]
        self.bidding = Bidding()
        self.current_player_index = 0
        self.tricks = []

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

    def play_card(self, player, card):
        for p_card in player.hand:
            if str(p_card) == card:
                self.tricks[-1].play_card(player, player.play_card(p_card))
                return True
        print("Invalid card. Try again.")
        return False

    def set_current_player_to_next_of_declarer(self):
        for i, player in enumerate(self.players):
            if player == self.bidding.declarer:
                self.current_player_index = (i + 1) % 4
                break


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
            if game.bidding.is_four_consecutive_passes():
                print("Four consecutive passes. The game ends with no contract.")
                return
            game.next_turn()

    print("Bidding phase is over.")
    print("Bidding history:\n", game.bidding.print_bidding_history())

    if game.bidding.declarer:
        game.set_current_player_to_next_of_declarer()

        # Playing phase
        print("\nPlaying Phase:")
        for _ in range(13):
            game.tricks.append(Trick())
            for _ in range(4):
                current_player = game.get_current_player()
                print(f"{current_player.name}'s turn to play.")
                print(f"Your hand: {current_player.show_hand()}")
                card = input("Enter the card to play (e.g., '2C'): ").strip().upper()
                if game.play_card(current_player, card):
                    game.next_turn()

            trick_winner = game.tricks[-1].determine_winner()
            print(f"{trick_winner.name} wins the trick!")

        print("Game over!")
        for player in game.players:
            tricks_won = sum(1 for trick in game.tricks if trick.determine_winner() == player)
            print(f"{player.name} won {tricks_won} tricks.")
    else:
        print("No valid contract was made. The game ends with no contract.")

if __name__ == "__main__":
    main()