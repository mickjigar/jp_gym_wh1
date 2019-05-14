import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np

class JpWh1(gym.Env):

    metadata = {'reder.modes': ['human']}

    def __init__(self):
        self.state = []
        for i in range(3):
            self.state += [[]]
            for j in range(3):
                self.state[i] += ['-']

        self.counter = 0
        self.done = 0
        self.add = [0,0]
        self.reward = 0

    def reset(self):

        for i in range(3):
            for j in range(3):
                self.state[i][j] = '-'

        self.counter = 0
        self.done = 0
        self.add = [0,0]
        self.reward = 0

        return self.state

    def render(self, mode='human', close=False):

        for i in range(3):
            for j in range(3):
                print(self.state[i][j], end=" ")
            print("")
