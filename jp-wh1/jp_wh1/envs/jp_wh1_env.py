import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
from jp_wh1.envs.jp_wh1_env_view import WarehouseView2D

class JpWh1(gym.Env):

    metadata = {'reder.modes': ['human','rgb_array']}

    ACTION = ["STAY", "IN", "OUT", "LEFT", "RIGHT"]

    def __init__(self,warehouse_file=None,warehouse_size=None):
        self.viewer = None

        if warehouse_file:
            self.warehouse_view = WarehouseView2D(warehouse_name="OpenAI Gym - Warehouse (%s)" % warehouse_file,
            warehouse_file_path=warehouse_file, screen_size=(640,640))

        elif warehouse_size:
            self.warehouse_view = WarehouseView2D(warehouse_name="OpenAI Gym - Warehouse (%d x %d)" % warehouse_size,
            warehouse_size=warehouse_size, screen_size=(640,640))

        else:
            #warehouse_size=(4,10)
            self.warehouse_view = WarehouseView2D(warehouse_name="OpenAI Gym - Default Warehouse (%d x %d)" % (16,600),
            screen_size=(640,640))
            #raise AttributeError("One must supply either a warehouse_file_path (str) or the warehouse_size (tuple of length 2)")

        self.warehouse_size = self.warehouse_view.warehouse_size

        #forward or backward in each dimension, pickup and dropoff are automatic
        #self.action_space = spaces.Discrete(2*len(self.warehouse_size)+1)
        self.action_space = spaces.MultiDiscrete([5,5])

        #observation is the x,y coordinate of the grid
        #low = np.zeros(len(self.warehouse_size),dtype=int)
        #high = np.array(self.warehouse_size,dtype=int) - np.ones(len(self.warehouse_size),dtype=int)

        #self.observation_space = spaces.Box(low,high,dtype=np.float32)
        self.observation_space = spaces.Box(low=-2.0, high=2.0, shape=(5,10), dtype=np.float32)

        #initial condition
        self.state = None
        self.steps_beyond_done = None
        self.done = False
        self.order = 0
        #simulation related variables
        self._seed()
        self.reset()

        #initialize relevant attributes
        self._configure()

    def __del__(self):
        self.warehouse_view.quit_game()

    def _configure(self, display=None):
        self.display = display

    def _seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def step(self, action):

        old_position_x_0 = self.warehouse_view.robot[0][0]
        old_position_y_0 = self.warehouse_view.robot[0][1]
        old_position_x_1 = self.warehouse_view.robot[1][0]
        old_position_y_1 = self.warehouse_view.robot[1][1]

        robot_0_value = -1.0
        robot_1_value = -1.0

        #if isinstance(action,int):
        print("ACTION IS: ", action)
        #if isinstance(action,(list,tuple, np.ndarray)):
        #   print("ACTION IS: ", action)

        self.warehouse_view.get_order()

        #self.warehouse_view.move_robot(self.ACTION[action])
        old_load = self.warehouse_view.move_robot(action, self.ACTION)
        # print("Old Load: ", old_load)
        # print("Order Array: ", self.warehouse_view.Orders.get_order_arr())

        old_value_0 = 0.0
        if self.warehouse_view.Orders.get_order_arr()[old_position_x_0][old_position_y_0] == 1.0 and old_load[0]:
            old_value_0 = 1.0
        old_value_1 = 0.0
        if self.warehouse_view.Orders.get_order_arr()[old_position_x_1][old_position_y_1] == 1.0 and old_load[1]:
            old_value_1 = 1.0
        #else:
        #   self.warehouse_view.move_robot(action)

        reward = [0,0]

        if self.warehouse_view.Orders.on_order(self.warehouse_view.robot[0][0], self.warehouse_view.robot[0][1]) and not old_load[0]:
            reward[0] = 1
            robot_0_value = 2.0
            self.warehouse_view.Orders.clear_order(self.warehouse_view.robot[0][0], self.warehouse_view.robot[0][1])
            #self.warehouse_view.pickup()

        elif self.warehouse_view.Orders.on_order(self.warehouse_view.robot[0][0], self.warehouse_view[0][1]) and old_load[0]:
            reward[0] = -0.1/(self.warehouse_size[0]*self.warehouse_size[1])
            #old_value = 1.0
            robot_0_value = -2.0

        elif np.array_equal(self.warehouse_view.robot[0], self.warehouse_view.entrance[0]) or np.array_equal(self.warehouse_view.robot[0], self.warehouse_view.entrance[1]):
            if not self.warehouse_view.is_loaded()[0]:
                #false dropoff
                reward[0] = -10
            else:
                #correct dropoff
                reward[0] = 20
                self.warehouse_view.dropoff(0)
                self.order += 1

        elif old_load[0]:
            reward[0] = -0.05/(self.warehouse_size[0]*self.warehouse_size[1])
            robot_0_value = 2.0

        else:
            reward[0] = -0.1/(self.warehouse_size[0]*self.warehouse_size[1])

        if self.warehouse_view.Orders.on_order(self.warehouse_view.robot[1][0], self.warehouse_view.robot[1][1]) and not old_load[1]:
            reward[1] = 1
            self.warehouse_view.Orders.clear_order(self.warehouse_view.robot[1][0], self.warehouse_view.robot[1][1])
            robot_1_value = 2.0
            #self.warehouse_view.pickup()

        elif self.warehouse_view.Orders.on_order(self.warehouse_view.robot[1][0], self.warehouse_view.robot[1][1]) and old_load[1]:
            reward[1] = -0.1/(self.warehouse_size[0]*self.warehouse_size[1])
            robot_1_value = -2.0
            #old_value_1 = 1.0

        elif np.array_equal(self.warehouse_view.robot[1], self.warehouse_view.entrance[0]) or np.array_equal(self.warehouse_view.robot[1], self.warehouse_view.entrance[1]):
            if not self.warehouse_view.is_loaded()[1]:
                #false dropoff
                reward[1] = -10
            else:
                #correct dropoff
                reward[1] = 20
                self.warehouse_view.dropoff(1)
                self.order +=1

        else:
            reward[1] = -0.1/(self.warehouse_size[0]*self.warehouse_size[1])

        if self.order == 1:
            done = True

        print("New Load: ", self.warehouse_view.is_loaded())

        self.state = copy.deepcopy(self.warehouse_view.Orders.get_order_arr())
        self.state[old_position_x_0][old_position_y_0] = old_value_0
        self.state[old_position_x_1][old_position_y_1] = old_value_1
        self.state[self.warehouse_view.robot[0][0]][self.warehouse_view.robot[0][1]] = robot_0_value
        self.state[self.warehouse_view.robot[1][0]][self.warehouse_view.robot[1][1]] = robot_1_value
        info = self.warehouse_view.update("human")

        print("Entrance: ", self.warehouse_view.entrance)
        print("Robot: ", self.warehouse_view.robot)
        print("Number of Orders Fulfilled: ", self.order)
        print("Reward: ", reward)
        print("Self.is_loaded: ", self.warehouse_view.is_loaded())

        return self.state, reward, self.done, info

    def reset(self):
        self.warehouse_view.reset_robot()
        self.state = np.zeros(2)
        self.steps_beyond_done = None
        self.done = False
        self.warehouse_view.Orders.reset()
        return self.state

    def is_game_over(self):
        return self.warehouse_view.game_over

    def render(self, mode='human', close=False):
        if close:
            self.warehouse_view.quit_game()
        return self.warehouse_view.update(mode)

class WarehouseEnvRandomDefault(JpWh1):

    def __init__(self):
        super (WarehouseEnvSampleRandomDefault,self).__init__()
