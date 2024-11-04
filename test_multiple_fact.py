from run_factory import run_factory, build, deliver, dist
from heuristic import calculate_time, heuristic_solution
from k_median_single_fact import k_median_single_factory
from k_center_single_fact import k_center_single_factory
import pulp as pl
import numpy as np
import scipy as sp
import json
import scipy.spatial.distance as spd
import itertools
import matplotlib.pyplot as plt

if __name__ == "__main__":
    #facts = [(0,0),(50,50),(100,100),(200,200)]
    #bays = [(50,50),(50,100),(100,50),(100,100),(100,150),(150,150)]
    # === Parameters ===
    # Inputs
    with open('test_data_20k.json', 'r') as file:
        data = json.load(file)

    bays=[]
    facts=[]
    for i in range (len(data['bays'])):
        bays.append((data['bays'][i]['x'], data['bays'][i]['y']))

    for i in range (len(data['factory_locations'])):
        facts.append((data['factory_locations'][i]['x'], data['factory_locations'][i]['y']))

    #Since there are 20k panels we will test using a bounding box:
    xmin=0
    xmax=600
    ymin=250
    ymax=1750
    bbox=[(xmin,ymin), (xmax,ymin), (xmax,ymax), (xmin,ymax), (xmin,ymin)]
    #remove bays not in the box
    bays_test1=[]
    for i in range(len(bays)):
        x=bays[i][0]
        y=bays[i][1]
        if x>=xmin and x<=xmax and y>=ymin and y<=ymax:
            bays_test1.append((x,y))
    

    best_factories, max_fact_time, factory_assignments = k_median_single_factory(bays_test1, facts, 3, 3)
    #print("Heuristic")
    #best_factories, max_fact_time, factory_assignments = heuristic_solution(bays_test1,facts, 3)
    #print(factory_assignments)
    #best_factories, max_fact_time, factory_assignments = k_center_single_factory(bays_test1, facts, 3, 3)

    plt.figure(figsize=(10,15))
    plt.scatter(*zip(*bays), marker='.', color='k', label='bays')
    plt.scatter(*zip(*facts), marker='x', color='k', label='factories')

    for factory, assigned_bays in factory_assignments.items():
        if factory in best_factories and len(assigned_bays) > 0:
            color=np.random.choice(range(256), size=3)/256
            plt.scatter(factory[0], factory[1], marker='o',s=70, color=color)
            plt.scatter(*zip(*assigned_bays), marker='.', color=color, label='bays assigned to factory '+str(factory))
    plt.plot(*zip(*bbox), color='blue', label='bounding box for test')
    plt.show()