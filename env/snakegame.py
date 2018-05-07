# -*- coding: utf-8 -*-
"""SnakeGame.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1b4WjWTWGGBgt_79hearLjrfmqJ5BcjGZ
"""

!pip install -q keras
!pip install gym

#@title Default title text
import numpy as np
from random import randint
from collections import deque

"""# **Snake Environment**"""

class SnakeEnv:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = np.zeros((x, y), dtype=int)
        self.reward_range = (0, 1)
        self.snake = deque([[5,5],[5,6],[5,7],[5,8],[5,9],[5,10]])
        self.score = 0
        self.gameover = 0
        self.reset()
        self.food()
        
    def food(self):
        a = randint(0,self.x-1)
        b = randint(0,self.y-1)
        if self.state[a][b] == 0:
            self.state[a][b] = 2
        else:
            self.food()
    
    def reset(self):
        self.state = np.zeros((self.x, self.y), dtype=int)
        self.snake = deque([[5,5],[5,6],[5,7],[5,8],[5,9],[5,10]])
        for i in self.snake:
            self.state[i[0]][i[1]] = 1
        self.state[0] = 3
        self.state[self.x - 1] = 3
        for i in range(self.x):
            self.state[i][0] = 3
            self.state[i][self.y - 1] = 3
            
    def render(self):
        for i in self.snake:
            self.state[i[0]][i[1]] = 1
    
    def step(self, action):
        state = self.state
        snake = self.snake
        head = snake[0]
        self.gameover = 0
        if action == 0:
            # collision with wall
            if state[head[0]][head[1]-1] == 3:
                self.gameover = 1
            # food
            if state[head[0]][head[1]-1] == 2:
                snake.appendleft([head[0], head[1]-1])
                self.food()
            # collision with self
            if state[head[0]][head[1]-1] == 1:
                self.gameover = 1
            # no obstruction
            if state[head[0]][head[1]-1] == 0:
                snake.appendleft([head[0], head[1]-1])
                state[snake[-1][0]][snake[-1][1]] = 0
                snake.pop()
    
        # Up
        if action == 1:
            # collision with wall
            if state[head[0]-1][head[1]] == 3:
                self.gameover = 1
            # food
            if state[head[0]-1][head[1]] == 2:
                snake.appendleft([head[0]-1, head[1]])
                self.food()
            # collision with self
            if state[head[0]-1][head[1]] == 1:
                self.gameover = 1
            # no obstruction
            if state[head[0]-1][head[1]] == 0:
                snake.appendleft([head[0]-1, head[1]])
                state[snake[-1][0]][snake[-1][1]] = 0
                snake.pop()

        # Right
        if action == 2:
            # collision with wall
            if state[head[0]][head[1]+1] == 3:
                self.gameover = 1
            # food
            if state[head[0]][head[1]+1] == 2:
                snake.appendleft([head[0], head[1]+1])
                self.food()
            # collision with self
            if state[head[0]][head[1]+1] == 1:
                self.gameover = 1
            # no obstruction
            if state[head[0]][head[1]+1] == 0:
                snake.appendleft([head[0], head[1]+1])
                state[snake[-1][0]][snake[-1][1]] = 0
                snake.pop()

        # Down
        if action == 3:
            # collision with wall
            if state[head[0]+1][head[1]] == 3:
                self.gameover = 1
            # food
            if state[head[0]+1][head[1]] == 2:
                snake.appendleft([head[0]+1, head[1]])
                self.food()
            # collision with self
            if state[head[0]+1][head[1]] == 1:
                self.gameover = 1
            # no obstruction
            if state[head[0]+1][head[1]] == 0:
                snake.appendleft([head[0]+1, head[1]])
                state[snake[-1][0]][snake[-1][1]] = 0
                snake.pop()
        self.render()
        self.score = len(snake) - 6
        return state, self.score, self.gameover

snek = SnakeEnv(15,15)

snek.state

snek.step(2)

snek.score

"""# Deep Q-**Network**"""

import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Conv2D, MaxPooling2D, Dropout, Flatten

class DQNAgent:
    def __init__(self):
        self.action_size = 4
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.model = self._build_model()
        
    def _build_model(self):
      
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Conv2D(32, (3, 3), padding='same', activation='relu', input_shape=(10, 15,3))
        model.add(Conv2D(32, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Conv2D(64, (3, 3), padding='same', activation='relu'))
        model.add(Conv2D(64, (3, 3), activation='relu'))
        model.add(MaxPooling2D(pool_size=(2, 2)))
        model.add(Dropout(0.25))

        model.add(Flatten())
        model.add(Dense(512, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(self.action_size, activation='linear'))
        
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        
        return model
      
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])  # returns action
      
    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
              target = reward + self.gamma * \
                       np.amax(self.model.predict(next_state)[0])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

episodes = 2000
step = 100

env = SnakeEnv(10, 15)
agent = DQNAgent()

for e in range(episodes):
  
  # reset
  env.reset()
  
  while not env.gameover:
    step = DQNAgent.act(env.state)
    env.step(step)

env = DQNAgent()

import time
j=0
t = time.time()
for i in range(100000):
    #j=0
    snek.reset()
    while 1:
        snek.step(randint(0,4))
        j+=1
        if snek.gameover == 1:
            break
print (time.time() - t)

from tensorflow.python.client import device_lib
device_lib.list_local_devices()
