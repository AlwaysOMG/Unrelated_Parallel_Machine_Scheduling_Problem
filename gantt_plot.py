# -*- coding: utf-8 -*-
"""
Created on Fri Sep  17 23:18:51 2021

@author: Yu Cheng, Lin @ CIM LAB
"""

# import packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


# cover INFO logging
plt.set_loglevel("WARNING")


# gantt
class Gantt:
    def __init__(self):
        self.gantt_data = {"M": [], "Order": [], \
                           "Start time": [], "Process time": [], 
                           "Due Date": []}
        self.makespan = 0

    def update_gantt(self, M, order, ST, PT, DD):
        self.gantt_data["M"].append(f"Machine {M}")
        self.gantt_data["Order"].append(order)
        self.gantt_data["Start time"].append(ST)
        self.gantt_data["Process time"].append(PT)
        self.gantt_data["Due Date"].append(DD)

    def draw_gantt(self, time):
        self.makespan = time
        # figure setting
        fig, axes = plt.subplots(figsize=(16, 6))
        axes.set_xlabel("Time")
        #axes.set_ylabel("Machine")
        axes.set_title("Gantt Chart")
        axes.set_xticks(np.arange(0, max(time + 1, 20), 10))
        # color set
        colors = list(mcolors.CSS4_COLORS.keys())
        # data processing
        machine = self.gantt_data["M"]
        order = self.gantt_data["Order"]
        start = self.gantt_data["Start time"]
        duration = self.gantt_data["Process time"]
        color = []
        for j in self.gantt_data["Order"]:
            if j == -1:
                color.append("#000000")
            else:
                if colors[j] == "black":
                    color.append(colors[-1]) # avoid black
                else:
                    color.append(colors[j])
        # draw bar
        axes.barh(y = machine, left = start, width = duration, \
                  height = 0.5, color = color, align = "center", \
                  alpha = 0.6, edgecolor = "black", linewidth = 1)
        # add order text
        for i in range(len(order)):
            text_x = start[i] + duration[i] / 2
            text_y = machine[i]
            text = f"J{order[i]}"
            if order[i] != -1:
                axes.text(text_x, text_y, text, fontsize=8, \
                          verticalalignment='center', \
                          horizontalalignment='center')

        # show plot
        plt.show()
    
    def output_report(self):
        df = pd.DataFrame(self.gantt_data)
        df = df[df["Order"] != -1]

        # Lateness
        df["completion_time"] = df["Start time"] + df["Process time"]
        df["lateness"] = df["completion_time"] - df["Due Date"]
        print("\nLateness:")
        print(df[["Order", "lateness"]])
        
        # Machine Utilization
        machine_utilization = df.groupby("M")["Process time"].sum() / self.makespan
        machine_utilization = machine_utilization.reset_index()
        machine_utilization.columns = ["Machine", "Utilization"]
        print("\nMachine Utilization:")
        print(machine_utilization)

        # makespan
        print("\nMakespan:")
        print(self.makespan)