# -*- coding: utf-8 -*-
"""
Created on Mon Sep  6 22:25:05 2021

@author: Yu Cheng, Lin @ CIM LAB
"""

# import packages
import numpy as np


# dispatching rule
class Dispatching_Rule:
    def FIFO(self, buffer):
        order = buffer[0]
        return order

    def LIFO(self, buffer):
        order = buffer[-1]
        return order

    def SPT(self, buffer, machine_ID):
        process_time_list = [order.process_time[machine_ID] for order in buffer]
        index = np.argmin(process_time_list)
        order = buffer[index]
        return order

    def MST(self, buffer, last_order_ID):
        if last_order_ID == -1:
            order = self.FIFO(buffer) # if no setup time, FIFO
        else:
            setup_time_list = [order.setup_time[last_order_ID] for order in buffer]
            index = np.argmin(setup_time_list)
            order = buffer[index]
        return order

    def EDD(self, buffer):
        due_date_list = [order.due_date for order in buffer]
        index = np.argmin(due_date_list)
        order = buffer[index]
        return order

    def LST(self, buffer, machine_ID, time_now):
        slack_time_list = [(order.due_date - time_now - order.process_time[machine_ID]) \
                           for order in buffer]
        index = np.argmin(slack_time_list)
        order = buffer[index]
        return order

    def CR(self, buffer, machine_ID, time_now):
        critical_ratio_list = [((order.due_date - time_now) / order.process_time[machine_ID]) \
                               for order in buffer]
        index = np.argmin(critical_ratio_list)
        order = buffer[index]
        return order