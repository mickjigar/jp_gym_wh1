#Determine how orders appear in the warehouse

import numpy as np
from collections import deque

class Orders:

    def __init__(self, warehouse_size=(16,600), classA=(0,1),classB=(0,0.5),classC=(0,0.1), dist="exp", warehouse_order_map_file_path=None,version=1):

        self.__classAmean =     classA[0]
        self.__classAstdev =    classA[1]
        self.__classBmean =     classB[0]
        self.__classBstdev =    classB[1]
        self.__classCmean =     classC[0]
        self.__classCstdev =    classC[1]

        self.__warehouse_size = warehouse_size

        if warehouse_order_map_file_path is None:
            self.__warehouse_order_class_map = self.make_warehouse_order_class_map(warehouse_size)

        else:
            if not os.path.exists(warehouse_order_map_file_path):
                dir_path = os.path.dirname(os.path.abspath(__file__))
                rel_path = os.path.join(dir_path, "order_map_samples", warehouse_order_map_file_path)

                if os.path.exists(rel_path):
                    warehouse_order_map_file_path = rel_path

                else:
                    raise FileExistsError("Cannot find %s." % warehouse_order_map_file_path)

            self.__warehouse_order_class_map = self.load_warehouse_order_class_map(warehouse_order_map_file_path)

        #efficient to store orders in an array according to location
        self.__orders = np.zeros(warehouse_size)
        self.num_orders = 0

    def make_warehouse_order_class_map(self, warehouse_size):
        #randomly assign each spot in the warehouse to class A, B, or C

        class_map = np.zeros(warehouse_size, dtype=int)

        class_map[1,0] = 0
        class_map[3,0] = 0

        for i in range(warehouse_size[0]):
            for j in range(warehouse_size[1]):
                if np.random.random_sample() < 0.05:
                    class_map[i][j] = 1
                elif np.random.random_sample() < 0.20:
                    class_map[i][j] = 2
                else:
                    class_map[i][j] = 3

        file_name = "default"
        np.save(file_name,class_map)

        return class_map

    def load_warehouse_order_class_map(self, warehouse_order_map_file_path):
        self.__warehouse_order_class_map = np.load(warehouse_order_map_file_path)

    def new_order(self, dist="test"):
        #Orders come in at specific rates
        #At each time step, one new order comes in

        x = int(self.__warehouse_size[0]*np.random_sample())
        y = int(self.__warehouse_size[1]*np.random_sample())
        qty = 0.0

        if [x,y]==[1,0] or [x,y]==[3,0]:
            return -1,-1,qty

        elif self.get_order_qty(x,y) == 0.0:
            order_class = self.__warehouse_order_class_map[x][y]

            if dist == "test":
                if order_class == 3:
                    if np.random.random_sample() < 0.05:
                        qty = 1

                if order_class == 2:
                    if np.random.random_sample() < 0.1:
                        qty = 1

                if order_class == 1:
                    if np.random.random_sample() < 0.25:
                        qty = 1

            elif dist == "exp":
                if order_class == 3:
                    qty = np.random.exponential(self.__classCmean)
                elif order_class == 2:
                    qty = np.random.exponential(self.__classBmean)
                if order_class == 1:
                    qty = np.random.exponential(self.__classAmean)


            elif dist == "normal":
                if order_class == 3:
                    qty = np.random.normal(self.__classCmean, self.__classCstdev)
                elif order_class == 2:
                    qty = np.random.normal(self.__classBmean, self.__classBstdev)
                if order_class == 1:
                    qty = np.random.normal(self.__classAmean, self.__classAstdev)

            self.set_order(x,y,qty)
            return x,y,qty

        else:
            return -1, -1, qty


    def clear_order(self,x,y):
        self.__orders[x][y] = 0
        self.num_orders -= 1

    def reset(self):
        self.__orders = np.zeros(self.__warehouse_size)

    def get_order_qty(self,x,y):
        return self.__orders[x][y]

    def on_order(self,x,y):

        if self.__orders[x][y] > 0:
            return True

        return False

    def get_order_arr(self):
        return self.__orders

    def set_order(self,x,y,qty):
        self.__orders[x][y] = qty
        self.num_orders += qty
