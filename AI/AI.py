import torch
import torch.nn as nn
import torch.optim as optim

# Constants
SUITS = ['C', 'D', 'H', 'S']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
BID_SUITS = ['C', 'D', 'H', 'S', 'NT']

VALID_BIDS = [f"{rank}{suit}" for rank in range(1, 8) for suit in BID_SUITS]


# Define Bidding Model
class BiddingModel(nn.Module):
    def __init__(self):
        super(BiddingModel, self).__init__()
        self.fc1 = nn.Linear(212, 128)  # 212 = 52 (hand) + 156 (bidding history) + 4 (role indicator)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 35)  # 35 possible bids including pass

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x


# Define Playing Model
class PlayingModel(nn.Module):
    def __init__(self):
        super(PlayingModel, self).__init__()
        self.fc1 = nn.Linear(524, 128)  # 524 = 52 (hand) + 156 (bidding history) + 1 (last bid value) + 5 (last bid suit) + 208 (cards played by 4 players) + 4 (role indicator)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, 52)  # 52 possible cards to play

    def forward(self, x, hand_mask):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        x = x + hand_mask  # Apply the mask to the logits
        return x


# Action selection with masking
def sample_action(action_logits, hand):
    mask = (hand - 1) * float('inf')
    action_logits = action_logits + mask
    action_probs = torch.softmax(action_logits, dim=-1)
    action = torch.multinomial(action_probs, 1).item()
    return action


# Example input for bidding model
hand = torch.zeros(52)
bidding_history = torch.zeros(156)
role_indicator = torch.tensor([0, 0, 1, 0])
state_bidding = torch.cat((hand, bidding_history, role_indicator))

bidding_model = BiddingModel()
output_bidding = bidding_model(state_bidding)
print(output_bidding)

# Example input for playing model
hand[10] = 1
hand[20] = 1

last_bid_value = torch.tensor([7])
last_bid_suit = torch.tensor([0, 1, 0, 0, 0])
cards_played_by_player1 = torch.zeros(52)
cards_played_by_player2 = torch.zeros(52)
cards_played_by_player3 = torch.zeros(52)
cards_played_by_player4 = torch.zeros(52)

state_playing = torch.cat((hand, bidding_history, last_bid_value, last_bid_suit, cards_played_by_player1,
                           cards_played_by_player2, cards_played_by_player3, cards_played_by_player4, role_indicator))

hand_mask = (hand - 1) * float('inf')

playing_model = PlayingModel()
output_playing = playing_model(state_playing, hand_mask)
print(output_playing)

# Example action selection
action_playing = sample_action(output_playing, hand)
print(f"Selected action: {action_playing}")


# Training loop for both models with episodic rewards
def train_models(bidding_model, playing_models, episodes):
    optimizer_bidding = optim.Adam(bidding_model.parameters(), lr=0.001)
    optimizer_playing = optim.Adam(sum([list(model.parameters()) for model in playing_models.values()], []), lr=0.001)
    loss_fn = nn.CrossEntropyLoss()

    for episode in range(episodes):
        # Initialize game state
        state_bidding = initialize_bidding_state()
        hand_mask = (hand - 1) * float('inf')

        # Bidding phase
        bidding_states = []
        bidding_actions = []
        for _ in range(max_bids):
            action_logits = bidding_model(state_bidding)
            action = sample_action(action_logits, hand)
            bidding_states.append(state_bidding)
            bidding_actions.append(action)
            next_state, done = step_bidding(action)
            if done:
                break
            state_bidding = next_state

        # Determine roles and start playing phase
        state_playing = initialize_playing_state()
        playing_states = {role: [] for role in playing_models}
        playing_actions = {role: [] for role in playing_models}
        rewards = []

        while not is_game_over(state_playing):
            current_player = get_current_player(state_playing)
            action_logits = playing_models[current_player.role].forward(state_playing, hand_mask)
            action = sample_action(action_logits, hand)
            playing_states[current_player.role].append(state_playing)
            playing_actions[current_player.role].append(action)
            next_state, done = step_playing(action)
            if done:
                break
            state_playing = next_state

        # Calculate rewards
        reward = calculate_reward(state_playing)
        rewards.append(reward)

        # Update bidding model
        optimizer_bidding.zero_grad()
        for state, action in zip(bidding_states, bidding_actions):
            action_logits = bidding_model(state)
            loss = loss_fn(action_logits.unsqueeze(0), torch.tensor([action])) * reward
            loss.backward()
        optimizer_bidding.step()

        # Update playing models
        optimizer_playing.zero_grad()
        for role in playing_models:
            for state, action in zip(playing_states[role], playing_actions[role]):
                action_logits = playing_models[role].forward(state, hand_mask)
                loss = loss_fn(action_logits.unsqueeze(0), torch.tensor([action])) * reward
                loss.backward()
        optimizer_playing.step()


# Initialize and train models
bidding_model = BiddingModel()
playing_models = {
    "quarterback": PlayingModel(),
    "partner": PlayingModel(),
    "defender1": PlayingModel(),
    "defender2": PlayingModel()
}

train_models(bidding_model, playing_models, episodes=10000)


# Placeholder functions to be implemented
def initialize_bidding_state():
    # Initialize the bidding state
    return torch.cat((torch.zeros(52), torch.zeros(156), torch.tensor([0, 0, 1, 0])))


def step_bidding(action):
    # Execute the bidding action and return the new state and done flag
    next_state = torch.cat((torch.zeros(52), torch.zeros(156), torch.tensor([0, 0, 1, 0])))
    done = False
    return next_state, done


def initialize_playing_state():
    # Initialize the playing state
    return torch.cat((torch.zeros(52), torch.zeros(156), torch.tensor([7]), torch.tensor([0, 1, 0, 0, 0]),
                      torch.zeros(52), torch.zeros(52), torch.zeros(52), torch.zeros(52), torch.tensor([0, 0, 1, 0])))


def step_playing(action):
    # Execute the playing action and return the new state and done flag
    next_state = torch.cat((torch.zeros(52), torch.zeros(156), torch.tensor([7]), torch.tensor([0, 1, 0, 0, 0]),
                            torch.zeros(52), torch.zeros(52), torch.zeros(52), torch.zeros(52),
                            torch.tensor([0, 0, 1, 0])))
    done = False
    return next_state, done


def get_current_player(state):
    # Return the current player based on the state
    class Player:
        def __init__(self, role):
            self.role = role

    return Player("quarterback")


def is_game_over(state):
    # Check if the game is over
    return False


def calculate_reward(state):
    # Calculate the reward based on the final state
    return 1  # Placeholder reward calculation
