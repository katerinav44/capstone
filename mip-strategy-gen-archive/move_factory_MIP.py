import pulp as pl
import numpy as np
from run_factory import *
import json
import matplotlib.pyplot as plt



def k_median_single_factory_moving(bays, facts, n_vehicles):
    facts_L = facts
    bays = np.array(bays)
    facts = np.array(facts)
    n_bays = len(bays)
    n_facts = len(facts)

    problem = pl.LpProblem("k_median_moving_factory", pl.LpMinimize)

    # === Decision Variables ===
    X = pl.LpVariable.dicts("service_bay", indices=(range(n_bays), range(n_facts)), lowBound=0, upBound=1, cat='Binary')
    Y = pl.LpVariable.dicts("move_factory", indices=range(n_facts), lowBound=0, upBound=1, cat='Binary')

    movement_penalty = 60 * 24  

    # === Objective Function ===
    total_cost = -movement_penalty

    # Add movement penalties for factories that are not the starting location
    for j in range(n_facts):
        total_cost += movement_penalty * Y[j]  # Movement penalty for all factories

    # Initial placement cost: No penalty for the selected starting factory
    total_cost += sum(run_factory(facts[j], [bays[i]], n_vehicles, True) * X[i][j] for j in range(n_facts) for i in range(n_bays))
    problem += total_cost, "Total_Cost"

    # === Constraints ===
    # Each bay is serviced by exactly one factory
    for i in range(n_bays):
        problem += sum(X[i][j] for j in range(n_facts)) == 1

    # A factory can only service a bay if it's "active"
    for j in range(n_facts):
        for i in range(n_bays):
            problem += X[i][j] <= Y[j]

    # === Solve the problem ===
    problem.solve()

    # === Output the results ===
    print(f"Status: {pl.LpStatus[problem.status]}")
    print(f"Objective Value: {pl.value(problem.objective)}")

    factory_assignments = {tuple(factory): [] for factory in facts_L}

    for j in range(n_facts):
        for i in range(n_bays):
            if X[i][j].varValue == 1:
                factory_assignments[tuple(facts_L[j])].append(tuple(bays[i]))

    #Compute construction time, and factory movement times
    factory_start_time = []
    factory_finish_time = []
    current_time = 0
    for i in range(n_facts):
        if factory_assignments[tuple(facts_L[i])]:
            factory_start_time.append(current_time)
            current_time += run_factory(facts_L[i], factory_assignments[facts_L[i]], n_vehicles, True)
            factory_finish_time.append(current_time)
            current_time += movement_penalty
        else:
            factory_start_time.append(-1)
            factory_finish_time.append(-1)
    #last element of movement_times is total construction time

    return factory_assignments, factory_start_time, factory_finish_time

if __name__ == "__main__":
    n_vehicles = 3
    
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
    ymin=750
    ymax=1750
    bbox=[(xmin,ymin), (xmax,ymin), (xmax,ymax), (xmin,ymax), (xmin,ymin)]
    #remove bays not in the box
    bays_test1=[]
    for i in range(len(bays)):
        x=bays[i][0]
        y=bays[i][1]
        if x>=xmin and x<=xmax and y>=ymin and y<=ymax:
            bays_test1.append((x,y))

    bays = [(1,1), (999999, 999999),(500,500), (0,0), (0,0)]
    facts = [(0, 0), (1000000, 1000000), (500,500)]
    factory_assignments, start_times, end_times=k_median_single_factory_moving(bays, facts, n_vehicles)
    print(factory_assignments)
    print(start_times)
    print(end_times)

    #plot results
    plt.figure(figsize=(10,15))
    plt.scatter(*zip(*bays), marker='.', color='k', label='bays')
    plt.scatter(*zip(*facts), marker='x', color='k', label='factories')

    for factory, assigned_bays in factory_assignments.items():
        if assigned_bays != []: #no bays assigned to factory
            i=list(factory_assignments.keys()).index(factory)
            color=np.random.choice(range(256), size=3)/256
            plt.scatter(factory[0], factory[1], marker='o',s=70, color=color)
            plt.scatter(*zip(*assigned_bays), marker='.', color=color, label='bays assigned to factory '+str(factory)+' at time t='+str(start_times[i]))
    plt.plot(*zip(*bbox), color='blue', label='bounding box for test')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    ttm=end_times[-1]
    plt.title('Total time: '+str(ttm) +'min')
    plt.show()
