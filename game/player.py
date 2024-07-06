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