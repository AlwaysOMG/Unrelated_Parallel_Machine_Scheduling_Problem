# -*- coding: utf-8 -*-
"""
Created on Fri Sep  3 21:02:05 2021

@author: Yu Cheng, Lin @ CIM LAB
"""

# import packages
import numpy as np
import pandas as pd


# parameter setting
SETUP_UL = 20
PT_UL = 100
AT_FACTOR = 50


# return global table (order + setup)
def generate(N, M, T_FACTOR):
    order = order_data(N, M, T_FACTOR)
    setup_time = setup_data(N)
    return order, setup_time

# return order data
def order_data(N, M, T_FACTOR):
    data = []
    for i in range(N):
        arrival_time = np.random.randint(1, (AT_FACTOR * N / M) + 1)
        process_time = []
        for j in range(M):
            time = np.random.randint(1, PT_UL + 1)
            process_time.append(time)
        due_date = arrival_time + T_FACTOR * np.mean(process_time)
        data.append([arrival_time, process_time, due_date])
    data.sort(key = lambda data:data[0])
    return data

# return setup data
def setup_data(N):
    data = []
    for i in range(N):
        sub_data = []
        for j in range(N):
            if(i == j):
                setup_time = 0
            else:
                setup_time = np.random.randint(1, SETUP_UL + 1)
            sub_data.append(setup_time)
        data.append(sub_data)
    return data


# main program
# data presentation in excel
if __name__ == "__main__":
    # writer setting
    path = './test_instance/UPMS_case.xlsx'
    writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
    # parameter setting
    np.random.seed(1)
    M = 3
    N = 8
    T_FACTOR = 1.5
    order, setup = generate(N, M, T_FACTOR)
    # data processing
    arrival_time = []
    process_time = []
    due_date = []
    for i in range(N):
        arrival_time.append(order[i][0])
        process_time.append(order[i][1])
        due_date.append(order[i][2])
    dic = {"arrival_time": arrival_time, "process_time": process_time, \
            "due_date": due_date}
    df0 = pd.DataFrame(dic)
    df1 = pd.DataFrame(setup)
    # write to excel
    df0.to_excel(writer, sheet_name = "order")
    df1.to_excel(writer, sheet_name = "setup")
    writer.close()