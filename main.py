# -*- coding: utf-8 -*-
"""
Created on Sat Sep  4 12:49:51 2021

@author: Yu Cheng, Lin @ CIM LAB
"""

# import packages
import numpy as np
import simpy
import logging


# import files
from dispatching_rule import Dispatching_Rule
from gantt_plot import Gantt


# logging setting
FORMAT = "{levelname} - {message}"
logging.basicConfig(level = logging.INFO, format = FORMAT, style = '{')


# entity
class Order:
    def __init__(self, ID, arrival_time, process_time, due_date, setup_time):
        # attribute
        self.ID             = ID
        self.arrival_time   = arrival_time
        self.process_time   = process_time
        self.due_date       = due_date
        self.setup_time     = setup_time


# resource
class Source:
    def __init__(self, factory, order_data, setup_data):
        # reference
        self.factory    = factory
        self.env        = factory.env
        # global table
        self.O = order_data
        self.S = setup_data
        # attribute
        self.N = len(order_data)
        # initial process
        self.env.process(self.arrival())
        
    def connect(self, queue):
        # reference
        self.queue      = queue
        
    def arrival(self):
        # release order one by one
        for i in range(self.N):
            # compute inter-arrival time and call a timeout
            inter_arrival_time = self.O[i][0] if i == 0 \
                else self.O[i][0] - self.O[i-1][0]
            if inter_arrival_time != 0:
                yield self.env.timeout(inter_arrival_time)
            # update next_arrival
            self.factory.next_arrival = self.O[i+1][0] if i < self.N-1 \
                else float('inf')
            # create an order and send to queue
            setup_time = [self.S[j][i] for j in range(self.N)]
            order = Order(i, self.O[i][0], self.O[i][1], self.O[i][2], 
                          setup_time)
            self.queue.pull(order)
            # record debug message
            self.factory.sim_record.append(
                f"{self.env.now}: order {order.ID} arrive.")
            # if batch arrival, release continually
            if i < self.N-1 and self.O[i][0] == self.O[i+1][0]:
                continue
            # confirm arrival over
            self.queue.arrival_over()
  

class Queue:
    def __init__(self, factory):
        # reference
        self.factory    = factory
        self.env        = factory.env
        # attribute
        self.buffer     = []
    
    def connect(self, dispatcher):
        # reference
        self.dispatcher = dispatcher
    
    def pull(self, order):
        # pull order to queue
        self.buffer.append(order)       

    def arrival_over(self):
        # call dispatcher
        self.dispatcher.check_dispatch()
        

class Dispatcher:
    def __init__(self, factory):
        # reference
        self.factory    = factory
        self.env        = factory.env
        self.DR         = Dispatching_Rule()
    
    def connect(self, queue, processor_list):
        # reference
        self.queue          = queue
        self.processor_list = processor_list
    
    def check_dispatch(self):
        # check machine status one by one
        for i in self.processor_list:
            if i.idle == True:
                if len(self.queue.buffer) == 1:
                    # without decision
                    order = self.queue.buffer.pop(0)
                    self.env.process(i.setup(order))
                elif len(self.queue.buffer) > 1:
                    # with decision
                    self.factory.decision_point.succeed()
                    self.factory.decision_point = self.env.event() # set future event
                break
                
    def dispatch(self, action):
        # dispatch according to action
        for i in range(len(self.processor_list)):
            if (self.processor_list[i].idle == True) and (len(self.queue.buffer) > 0):
                if action == 0:
                    order = self.DR.FIFO(self.queue.buffer)
                elif action == 1:
                    order = self.DR.LIFO(self.queue.buffer)
                elif action == 2:
                    order = self.DR.SPT(self.queue.buffer, i)
                elif action == 3:
                    order = self.DR.MST(self.queue.buffer, 
                                        self.processor_list[i].last_order_ID)
                elif action == 4:
                    order = self.DR.EDD(self.queue.buffer)
                elif action == 5:
                    order = self.DR.LST(self.queue.buffer, i, self.env.now)
                elif action == 6:
                    order = self.DR.CR(self.queue.buffer, i, self.env.now)
                self.queue.buffer.remove(order)
                self.env.process(self.processor_list[i].setup(order))
                    

class Processor:
    def __init__(self, factory, ID):
        # reference
        self.factory    = factory
        self.env        = factory.env
        # attribute
        self.ID                 = ID
        self.idle               = True
        self.MAT                = 0
        self.last_order_ID      = -1
        self.current_order_ID   = -1
        self.latest_setup_time  = -1

    def connect(self, dispatcher, sink):
        # reference
        self.dispatcher = dispatcher
        self.sink       = sink
    
    def setup(self, order):
        # calculate reward
        self.factory.calculate_reward(order, self)
        # processor become busy
        self.idle = False
        if self.last_order_ID != -1:
            # draw setup gantt bar
            self.factory.gantt.update_gantt(
                self.ID, -1, self.env.now, order.setup_time[self.last_order_ID], -1)
            # record debug message
            self.factory.sim_record.append(
                f"{self.env.now}: order {order.ID} setup at machine {self.ID}.")
            # call a timeout
            yield self.env.timeout(order.setup_time[self.last_order_ID])
            # update attribute
            self.latest_setup_time = self.env.now
        # start process
        self.env.process(self.process(order))
    
    def process(self, order):
        # draw process gantt bar
        self.factory.gantt.update_gantt(
            self.ID, order.ID, self.env.now, order.process_time[self.ID], order.due_date)
        # update attribute
        self.factory.order_status[order.ID] = 0
        self.MAT = self.env.now + order.process_time[self.ID]
        self.current_order_ID = order.ID
        # start process and record debug message
        self.factory.sim_record.append(
            f"{self.env.now}: order {order.ID} start at machine {self.ID}.")
        yield self.env.timeout(order.process_time[self.ID])
        self.factory.sim_record.append(
            f"{self.env.now}: order {order.ID} finish at machine {self.ID}.")
        # update attribute
        self.idle = True
        self.last_order_ID = order.ID
        self.current_order_ID = -1 
        self.factory.order_status[order.ID] = -1
        # try to get more order
        self.sink.finish_order(order)
        if self.factory.next_arrival != self.env.now:
            self.dispatcher.check_dispatch()


class Sink:
    def __init__(self, factory, N):
        # reference
        self.factory    = factory
        self.env        = factory.env
        # attribute
        self.throughput     = 0
        self.terminal_num   = N
                
    def finish_order(self, order):        
        # finish
        self.throughput += 1
        del order
        # check terminal
        if self.throughput == self.terminal_num:
            self.factory.decision_point.succeed() # to stop the step
            self.factory.terminal.succeed()
            self.factory.makespan = self.env.now


class Factory: 
    def build(self, N, M, order_data, setup_data):
        # environment
        self.env = simpy.Environment()
        # attribute
        self.N                  = N
        self.M                  = M
        self.order_data         = order_data
        self.setup_data         = setup_data
        self.makespan           = 0
        self.next_arrival       = order_data[0][0]
        self.step_reward        = 0
        self.order_status       = [1 for i in range(N)] # waiting
        # build
        self.source         = Source(self, order_data, setup_data)
        self.queue          = Queue(self)
        self.dispatcher     = Dispatcher(self)
        self.processor_list = [Processor(self, i) for i in range(M)]
        self.sink           = Sink(self, N)
        # event
        self.decision_point = self.env.event()
        self.terminal       = self.env.event()
        # record
        self.sim_record     = []
        self.step_record    = []
        # gantt plot
        self.gantt = Gantt()
        # initialize
        self.initialize()
    
    def initialize(self):
        # connect resource
        self.source.connect(self.queue)
        self.queue.connect(self.dispatcher)
        self.dispatcher.connect(self.queue, self.processor_list)
        for i in self.processor_list:
            i.connect(self.dispatcher, self.sink)
        
    def observation(self):
        # state data
        m0 = []
        for i in range(self.N):
            l = []
            l.append(self.order_data[i][0])
            for j in range(self.M):
                l.append(self.order_data[i][1][j])
            l.append(self.order_data[i][2])
            l.append(self.order_status[i])
            m0.append(l)
        # processor data
        m1 = []
        for i in range(self.M):
            l = []
            l.append(self.processor_list[i].MAT)
            l.append(self.processor_list[i].last_order_ID)
            l.append(self.processor_list[i].current_order_ID)
            if (self.processor_list[i].latest_setup_time == -1):
                l.append(0)    
            else:
                l.append(round(self.env.now, 2) - self.processor_list[i].latest_setup_time)
            m1.append(l)
        # setup data
        m2 = self.setup_data
        m0 = np.array(m0)
        m1 = np.array(m1)
        m2 = np.array(m2)
        return m0, m1, m2
        
    def calculate_reward(self, order, processor):
        if processor.last_order_ID == -1:
            total_time = order.process_time[processor.ID]
            upper_bound = max(order.process_time)
        else:
            wait_setup = order.setup_time[processor.last_order_ID]
            total_time = wait_setup + order.process_time[processor.ID]
            upper_bound = max(order.setup_time) + max(order.process_time)
        self.step_reward += (upper_bound - total_time)


    def new_reward(self, done):
        if done:
            MAT_list = []
            for i in range(self.M):
                MAT_list.append(self.processor_list[i].MAT)
                reward = 1000 / max(MAT_list)
        else:
            reward = 0
        return reward
        
    
    # start with this function 
    def reset(self, N, M, order_data, setup_data):
        self.build(N, M, order_data, setup_data)
        self.env.run(self.decision_point)
        m1, m2, m3 = self.observation() # state at t
        return [m1, m2, m3]
    
    # run with this process
    def step(self, action):
        old_m1, old_m2, old_m3 = self.observation()
        old_state = [old_m1, old_m2, old_m3] # state at t
        self.dispatcher.dispatch(action)
        self.env.run(self.decision_point) # run until next input of action
        m1, m2, m3 = self.observation() 
        state = [m1, m2, m3] # state at t+1
        done = self.terminal.triggered
        reward = self.new_reward(done) # reward at t
        self.store_transition(old_state, action, reward, state)
        self.step_reward = 0
        return state, reward, done
    
    def show_debug(self):
        # show event of simulation in logging
        for i in self.sim_record:
            logging.info(i)
        
    def store_transition(self, old_state, action, reward, new_state):
        # record state, action, reward
        dic = {'old state': old_state, 'action': action, 
               'reward': reward, 'new state': new_state}
        self.step_record.append(dic)
        
    def show_transition(self):
        # show state, action, reward of RL in console
        counter = 1
        for i in self.step_record:
            old_state = i['old state']
            action = i['action']
            reward = i['reward']
            new_state = i['new state']
            print(f"=====transition {counter}=====")
            print(f"old state:\n{old_state}")
            print(f"action: {action}")
            print(f"reward: {reward}")
            print(f"new state:\n{new_state}")
            counter += 1

# main program
# debug simulation with logging
if __name__ == '__main__':
    # import files
    from test_instance_generator import generate
    # parameter setting
    np.random.seed(2)
    N = 8
    M = 3
    T_FACTOR = 1.5
    ORDER, SETUP = generate(N, M, T_FACTOR)
    # start simulation
    env = Factory()
    env.reset(N, M, ORDER, SETUP)
    while True:
        action = 0
        state, _, done = env.step(action)
        if done:
            break
    env.show_debug()
    #env.show_transition()
    env.gantt.draw_gantt(env.makespan)
    env.gantt.output_report()
    
