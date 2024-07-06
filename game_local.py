import pygame
import random

"""
1 C - club (♣)
1 D - diamond (♦)
1 H - heart (♥)
1 S - spade (♠)
1 N - notrump (NT)

"""

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

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank} {self.suit}"

class Deck:
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self):
        self.cards = [Card(suit, rank) for suit in self.suits for rank in self.ranks]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 800
BG_COLOR = (34, 139, 34)  # Green background for the table
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (0, 128, 0)
BUTTON_HOVER_COLOR = (0, 255, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
HAND_AREA_HEIGHT = 150

BIDDING_OPTIONS = [
    "1C", "1D", "1H", "1S", "1NT",
    "2C", "2D", "2H", "2S", "2NT",
    "3C", "3D", "3H", "3S", "3NT",
    "4C", "4D", "4H", "4S", "4NT",
    "5C", "5D", "5H", "5S", "5NT",
    "6C", "6D", "6H", "6S", "6NT",
    "7C", "7D", "7H", "7S", "7NT",
]

def draw_text(screen, text, font, color, rect, aa=False, bkg=None):
    rect = pygame.Rect(rect)
    y = rect.top
    line_spacing = -2

    # Get the height of the font
    font_height = font.size("Tg")[1]

    while text:
        i = 1

        # Determine if the row of text will be outside our area
        if y + font_height > rect.bottom:
            break

        # Determine maximum width of line
        while font.size(text[:i])[0] < rect.width and i < len(text):
            i += 1

        # If we've wrapped the text, then adjust the wrap to the last word
        if i < len(text):
            i = text.rfind(" ", 0, i) + 1

        # Render the line and blit it to the surface
        if bkg:
            image = font.render(text[:i], aa, color, bkg)
            image.set_colorkey(bkg)
        else:
            image = font.render(text[:i], aa, color)

        screen.blit(image, (rect.left, y))
        y += font_height + line_spacing

        # Remove the text we just blitted
        text = text[i:]

    return text

def draw_button(screen, text, font, rect, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if rect.collidepoint(mouse):
        pygame.draw.rect(screen, BUTTON_HOVER_COLOR, rect)
        if click[0] == 1 and action is not None:
            action()
    else:
        pygame.draw.rect(screen, BUTTON_COLOR, rect)

    text_surf = font.render(text, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Bridge Game")

    game = GameLogic()
    game.start_game()

    font = pygame.font.Font(None, 36)

    bidding_history_text = ""

    def show_bidding_history():
        nonlocal bidding_history_text
        bidding_history_text = game.print_bidding_history()

    def pass_bid():
        current_player = game.game_state.get_current_player()
        game.bid(current_player, None)
        game.game_state.next_turn()

    def place_bid(bid):
        current_player = game.game_state.get_current_player()
        game.bid(current_player, bid)
        game.game_state.next_turn()

    running = True
    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw bidding buttons
        for i, bid in enumerate(BIDDING_OPTIONS):
            row = i // 5
            col = i % 5
            button_rect = pygame.Rect(50 + col * 140, 50 + row * 50, 130, 40)
            draw_button(screen, bid, font, button_rect, action=lambda b=bid: place_bid(b))

        # Draw pass button
        pass_button_rect = pygame.Rect(50, 500, 200, 50)
        draw_button(screen, "Pass", font, pass_button_rect, action=pass_bid)

        # Draw show bidding history button
        show_bidding_history_button_rect = pygame.Rect(300, 500, 200, 50)
        draw_button(screen, "Show Bidding History", font, show_bidding_history_button_rect, action=show_bidding_history)

        # Display hand
        current_player = game.game_state.get_current_player()
        hand_text = game.print_current_player_hand()
        draw_text(screen, f"Hand: {hand_text}", font, WHITE, pygame.Rect(50, 550, 700, HAND_AREA_HEIGHT))

        # Display bidding history
        draw_text(screen, f"Bidding History:\n{bidding_history_text}", font, WHITE, pygame.Rect(50, 450, 700, 50))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()