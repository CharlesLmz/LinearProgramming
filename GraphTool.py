# read data from dateset

import numpy as np
import matplotlib.pyplot as plt

class Graph():
    def __init__(self, file_name, limit_node_num = None):
        self.read_data(file_name, limit_node_num) # read data from file
        self.preprocess_data() # preprocess data
    
    def read_data(self, file_name, limit_node_num):
        """
        read VRPTW data from dataset
        input: file_name
        output: problem object (including (int)vehicleNum, (int capacity, (numpy-array[25, 6])customers)
                ps:customers include x, y, demand, ready_time, due_time, service_time
        """
        with open(file_name) as file_object:
            lines = file_object.readlines()
        
        # load vehicle setting
        vehicle = list(map(int, lines[4].split()))
        vehicleNum, capacity = vehicle

        # load customers setting
        location = []
        demand = []
        readyTime = []
        dueTime = []
        serviceTime = []
        for line in lines[9:]:
            cust = list(map(int, line.split()))
            if cust == []:
                continue
            location.append(cust[1:3])
            demand.append(cust[3])
            readyTime.append(cust[4])
            dueTime.append(cust[5])
            serviceTime.append(cust[6])

        # save data
        self.vehicleNum = vehicleNum
        self.capacity = capacity
        self.location = np.array(location[:limit_node_num])
        self.demand = np.array(demand[:limit_node_num])
        self.readyTime = np.array(readyTime[:limit_node_num])
        self.dueTime = np.array(dueTime[:limit_node_num])
        self.serviceTime = np.array(serviceTime[:limit_node_num])
     
    def preprocess_data(self):
        self.nodeNum = len(self.location) # record nodeNum
        self.cal_disMatrix() # calculate distances between each points
        self.cal_feasibleNodeSet() # filter feasible arc according to time window

    def cal_disMatrix(self):
        """
        calculate distances between each points
        """
        self.disMatrix = np.zeros((self.nodeNum, self.nodeNum))
        for i in range(self.nodeNum):
            for j in range(self.nodeNum):
                self.disMatrix[i, j] = np.linalg.norm(self.location[i] - self.location[j])        
        self.timeMatrix = self.disMatrix # speed=1 in solomon

    def cal_feasibleNodeSet(self):
        """
        filter feasible arc according to time window
        """
        self.feasibleNodeSet = [[] for _ in range(self.nodeNum)]
        self.availableNodeSet = [[] for _ in range(self.nodeNum)]
        self.infeasibleNodeSet = [[] for _ in range(self.nodeNum)]
        for i in range(self.nodeNum):
            for j in range(self.nodeNum):
                if i == j:
                    continue
                if self.readyTime[i] + self.serviceTime[i] + self.disMatrix[i, j] <= self.dueTime[j]:
                    self.feasibleNodeSet[i].append(j)
                    self.availableNodeSet[j].append(i)
                else:
                    self.infeasibleNodeSet[i].append(j)
       
    def evaluate(self, routes, show=False):
        obj = 0
        visit_customer = np.zeros(self.nodeNum)
        # check each routes
        for route in routes:
            # check capacity constraint
            load = sum(self.demand[route])
            if load > self.capacity:
                print("Infeasible Solution: break capacity constraint")
                return np.inf
            # check time window / pass all customers
            t = 0
            for i in range(1, len(route)):
                pi = route[i-1]
                pj = route[i]
                t_ = t + self.serviceTime[pi] + self.timeMatrix[pi, pj]
                if t_ > self.dueTime[pj]:
                    print("Infeasible Solution: break time window")
                    return np.inf 
                t = max(t_, self.readyTime[pj])
                visit_customer[pj] = 1
            # calculate objective value
            dist = sum(self.disMatrix[route[:-1], route[1:]])
            obj += dist
        if sum(visit_customer) < self.nodeNum:
            print("Infeasible Solution: haven't visit all points")
            return np.inf
        if show:
            print("Feasible Solution: obj = {}".format(obj))
        return obj

    def render(self, routes):
        plt.figure()
        plt.scatter(self.location[1:, 0], self.location[1:, 1])
        plt.scatter(self.location[0:1, 0], self.location[0:1, 1], s = 150, c = 'r', marker='*')
        for route in routes:
            plt.plot(self.location[route, 0], self.location[route, 1])
        plt.show()

class GraphForAugerat(Graph):
    def __init__(self, file_name):
        self.read_data(file_name) 
        self.preprocess_data()

    def read_data(self, file_name):
        """
        read VRPTW data from Augerat dataset
        input: file_name
        output: problem object (including (int)vehicleNum, (int) capacity, (numpy-array[25, 6])customers)
                ps:customers include x, y, demand
        """
        with open(file_name) as file_object:
            lines = file_object.readlines()
        
        # load vehicle setting
        vehicleNum = nodeNum = int(lines[3].split()[2])
        capacity = int(lines[5].split()[2])

        # load customers setting
        location = []
        demand = []
        for line in lines[7:7+nodeNum]:
            cust = list(map(int, line.split()))
            location.append(cust[1:3])
        for line in lines[8+nodeNum:8+2*nodeNum]:
            cust = list(map(int, line.split()))
            demand.append(cust[1])
        self.vehicleNum = vehicleNum
        self.nodeNum = len(location)
        self.capacity = capacity
        self.location = np.array(location)
        self.demand = np.array(demand)

    def preprocess_data(self):
        self.nodeNum = len(self.location)
        self.cal_disMatrix()

if __name__ == "__main__":
    file_name = "solomon_100/C106.txt"
    prob = Graph(file_name)
    file_name = "Augerat/A-n32-k5.vrp"
    prob = GraphForAugerat(file_name)