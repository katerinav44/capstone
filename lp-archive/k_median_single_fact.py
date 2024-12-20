from run_factory import run_factory, build, deliver, dist, convert_text_coordinates
from run_factory_float import run_factory_float
import pulp as pl
import numpy as np
import scipy as sp
import json
import scipy.spatial.distance as spd
import matplotlib.pyplot as plt



# === Decision Variables ===

def k_median_single_factory(bays, facts, n_vehicles, k):
    print("start lp")
    bays_list=bays
    print(len(bays_list))
    facts_list=facts
    bays = np.array(bays_list)
    facts = np.array(facts_list) #the most annoying way of doing this I know
    n_bays = len(bays)
    n_facts = len(facts) # we should also account for the fact that there may be less factories than available factory locations
    problem = pl.LpProblem("k_median", pl.LpMinimize)

    d = []
    for fact in facts_list:
        d.append(run_factory(fact, bays_list, n_vehicles, False))


    # X and Y decision variables
    X = pl.LpVariable.dicts("bay_factory", indices = (range(len(bays)), range(len(facts))), lowBound=0, upBound=1, cat='Binary')
    Y = pl.LpVariable.dicts("factory_chosen", indices = range(len(facts)), lowBound=0, upBound=1, cat='Binary')
    # define z for (3)
    #z = pl.LpVariable("max_run_fact_time")

    # === Objective Function ===
    # Minimize k-median distance as a heuristic for time
    problem += (
        # (0) Standard using sum of manhattan distances
        #sum(sum(spd.cityblock(bays[i], facts[j]) * X[i][j] for j in range(n_facts)) for i in range(n_bays))

        # (1) using run factory - this only works for single factory
        # sum(d[j] * Y[j] for j in range(n_facts))

        # (Attempt 2 - run_factory k > 1) 
        sum(run_factory(facts_list[j], [bays_list[i] for i in range(n_bays) if X[i][j] == 1], 1, True) for j in range(n_facts)) 
        # (3) using run factory on a selection of bays
        #z
    ), "k_median"

    # === Constraints ===
    for i in range(n_bays):
        problem += sum(X[i][j] for j in range(n_facts)) == 1 # each bay i serviced by 1 factory

    problem += sum(Y[j] for j in range(n_facts)) == k # k factories chosen

    for j in range(n_facts):
        # Define constraint for (3)
        #problem += run_factory(facts_list[j], [bays_list[i] for i in range(n_bays) if X[i][j] == 1], 1, True) <= z
        problem += sum(X[i][j] for i in range(n_bays)) <= Y[j] * n_bays # each factory j services less than all bays

    # === Solve the problem ===
    problem.solve()

    # === Output the results ===
    print(f"Status: {pl.LpStatus[problem.status]}")
    best_factories=[]
    factory_assignments = {factory: [] for factory in facts_list}
    
    for j in range(n_facts):
        for i in range(n_bays):
            if X[i][j].varValue == 1:
                factory_assignments[facts_list[j]].append(bays_list[i])
    #print(factory_assignments)

    # In single factory case, this prints out time for all factories
    if k == 1:
        for j in range(n_facts):
            fact_time = run_factory(facts_list[j], bays_list, n_vehicles, True)
            fact_dist = sum(spd.cityblock(bays[i], facts[j]) for i in range(n_bays))
            print(f"Factory: {facts[j]}, Time: {fact_time}, Total Distance: {fact_dist}")

            if Y[j].varValue == 1:
                print(f"Factory Chosen: {facts[j]}")
                best_factories.append(facts[j])
                max_fact_time = fact_time
                #factory_assignments[facts_list[j]] = bays_list
    else:
        max_fact_time = run_factory_float(facts_list, factory_assignments, n_vehicles)
        for j in range(n_facts):
            if Y[j].varValue == 1:
                best_factories.append(facts_list[j])
    #print(factory_assignments)
    return best_factories, max_fact_time, factory_assignments


#k_median_single_factory(bays_test1, facts, 3, 1)
#facts = [(0,0),(50,50),(100,100)]
#bays = [(50,50),(50,100),(100,50),(100,100),(100,150),(150,150)]
#k_median_single_factory(bays, facts, 1, 1)

if __name__ == "__main__":
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
    
    #facts = [(0,0),(50,50),(100,100)]
    #bays_test1 = [(50,50),(50,100),(100,50),(500,500),(600,600),(700,700)]

    best_factories, max_fact_time, factory_assignments = k_median_single_factory(bays_test1, facts, 3, 3)
    print(best_factories)
    print(factory_assignments)
    run_factory_float(facts, factory_assignments, 3)

    # X = [[0,1],[1,0]]
    # bays_list = [(1,0),(2,2)]
    # facts_list = [(0,0),(1,10)]

    #print(factory_assignments)
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

    # n_bays = len(bays_list)
    # n_facts = len(facts_list)
    #print([bays_list[a] for a in range(n_bays) if X[a][0] == 1])
    #run_factory([0,0],[bays_list[a] for a in range(n_bays) if X[a][0] == 1], 1, True)
    #print(max([run_factory(facts_list[j], [bays_list[i] for i in range(n_bays) if X[i][j] == 1], 1, True) for j in range(n_facts)]))

