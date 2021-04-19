import torch
import numpy as np
import random
from Snake import SnakeGame, Direction, Point
from collections import deque #Doubly Ended Queue
from Qlearner import QTrainer, Linear_Q

MAX_MEMORY = 100_000
BATCH = 10_000
LR = 0.001

class Agent:
    def __init__(self):
        self.num_of_play = 0 #number of play
        self.randomness = 0 #random rate
        self.gamma = 0.9 #Gamma rate for the how much we care about the future
        self.model = Linear_Q(11, 256, 3) #Network art.
        self.memory = deque(maxlen=MAX_MEMORY) #Doubly Ended Queue
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma) #Trainer for the model

    def geting_states(self, game):
        head = game.snake[0]

        #The points of view
        point_left = Point(head.x - 40, head.y)
        point_right = Point(head.x + 40, head.y)
        point_up = Point(head.x, head.y - 40)
        point_down = Point(head.x, head.y + 40)

        #Directions that snake goes
        direction_left = game.direction == Direction.LEFT
        direction_right = game.direction == Direction.RIGHT
        direction_up = game.direction == Direction.UP
        direction_down = game.direction == Direction.DOWN

        state = [

            #Moving Direction
            direction_left,
            direction_right,
            direction_up,
            direction_down,

            #There is a danger in front
            direction_left and game.finish(point_left) or
            direction_right and game.finish(point_right) or
            direction_up and game.finish(point_up) or
            direction_down and game.finish(point_down),

            #Danger on the right
            direction_up and game.finish(point_right) or
            direction_right and game.finish(point_down) or
            direction_down and game.finish(point_left) or
            direction_left and game.finish(point_up),

            #Danger on the left

            direction_up and game.finish(point_left) or
            direction_down and game.finish(point_right) or
            direction_left and game.finish(point_down) or
            direction_right and game.finish(point_up),

            #Where is the food ha!

            game.food.x < game.head.x,
            game.food.x > game.head.x,
            game.food.y < game.head.y,
            game.food.y > game.head.y
        ]
        return np.array(state,dtype=int) #It is translate boolen to 1 and 0

    def making_action(self, state):
        self.randomness = 80 - self.num_of_play #Randomness will decrease when number of play increase
        final_move = [0, 0, 0]
        # If random number smaller than randomness, make a random move
        if random.randint(0, 200) < self.randomness:
            inx = random.randint(0, 2)
            final_move[inx] = 1
        # Predict the next move if random number bigger than randomness
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            idx = torch.argmax(prediction).item()
            final_move[idx] = 1

        return final_move

    def remember_old_one(self, state, action, reward, next_state, over): #appending memory for gain past experience
        self.memory.append((state, action, reward, next_state, over))

    def train_long(self): #training old games
        if len(self.memory) > BATCH: # if memory is greater than wanted experience
            sample = random.sample(self.memory, BATCH) #take random experince from memory
        else:
            sample = self.memory # if smaller than take all

        # Looping the states, actions, rewards, next_states, overs from samples
        states, actions, rewards, next_states, overs = zip(*sample)
        self.trainer.train_step(states, actions, rewards, next_states, overs)

    #training experince now
    def train_short(self, state, action, reward, next_state, over):
        self.trainer.train_step(state, action, reward, next_state, over)

def trainer():
    agent = Agent()
    game = SnakeGame()
    score = 0
    record = 0

    while True:
        state_past = agent.geting_states(game) #take a state from the game

        taken_action = agent.making_action(state_past)  #take an action using state

        reward, game_over, score = game.play(taken_action) #take the consequences of that action

        state_new = agent.geting_states(game) #take the new state from the game

        agent.train_short(state_past, taken_action, reward, state_new, game_over) #train the network

        agent.remember_old_one(state_past, taken_action, reward, state_new, game_over) #Remember the experience

        if game_over:
            game.reset()
            agent.num_of_play += 1
            agent.train_long() #Use the past experience for the game
            print(agent.num_of_play)
        if score > record:
            record = score
            agent.model.save()

if __name__ == "__main__":
    trainer()