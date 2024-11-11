import pulp as pl
import numpy as np
from run_factory import *
import json
import matplotlib.pyplot as plt



def k_median_single_factory_moving(bays, facts, n_vehicles, n_factories):
    facts_L = facts
    bays = np.array(bays)
    facts = np.array(facts)
    n_bays = len(bays)
    n_locations = len(facts)

    problem = pl.LpProblem("k_median_moving_factory", pl.LpMinimize)

    # === Decision Variables ===
    X = pl.LpVariable.dicts("service_bay", indices=(range(n_bays), range(n_factories), range(n_locations)), lowBound=0, upBound=1, cat='Binary')
    Y = pl.LpVariable.dicts("move_factory", indices=(range(n_factories), range(n_locations)), lowBound=0, upBound=1, cat='Binary')
    #Y needs to be n_factories by n_facts
    max_time = pl.LpVariable('max_time',lowBound = 0, cat='Continuous')

    problem += max_time #add objective function to problem

    movement_penalty = 60 * 24  

    # === Objective Function ===
    
    # time to build with each factory
    for j in range(n_factories):
        problem += (sum(Y[j][k] for k in range(n_locations))-1) * movement_penalty + sum(run_factory(facts[k], [bays[i]], n_vehicles, True) * X[i][j][k] for k in range(n_locations) for i in range(n_bays))<= max_time

    # === Constraints ===
    # Each bay is serviced by exactly one factory
    for i in range(n_bays):
        problem += sum(X[i][j][k] for k in range(n_locations) for j in range(n_factories)) == 1

    # each location is services by exactly one factory
    for k in range(n_locations):
        problem += sum(Y[j][k] for j in range(n_factories)) <= 1

    # A factory can only service a bay if it's "active"
    for i in range(n_bays):
        for j in range(n_factories):
            for k in range(n_locations):
                problem += X[i][j][k] <= Y[j][k]

    # === Solve the problem ===
    problem.solve()

    # === Output the results ===
    print(f"Status: {pl.LpStatus[problem.status]}")
    print(f"Objective Value: {pl.value(problem.objective)}")

    factory_assignments = {j:{tuple(loc): [] for loc in facts_L} for j in range(n_factories)}

    x = np.zeros((n_bays, n_factories, n_locations))
    y = np.zeros((n_factories, n_locations))
    for k in range(n_locations):
        for j in range(n_factories):
            if Y[j][k].varValue == 1:
                y[j][k] = 1
            for i in range(n_bays):
                if X[i][j][k].varValue == 1:
                    x[i][j][k] = 1
                    factory_assignments[j][tuple(facts_L[k])].append(tuple(bays[i]))

    #Compute construction time, and factory movement times
    factory_start_time = {}
    factory_finish_time = {}

    for j in range(n_factories):
        current_time = 0
        factory_start_time[j] = []
        factory_finish_time[j] = []
        for k in range(n_locations):
            if factory_assignments[j][tuple(facts_L[k])]:
                factory_start_time[j].append(current_time)
                current_time += run_factory(facts_L[k], factory_assignments[j][facts_L[k]], n_vehicles, True)
                factory_finish_time[j].append(current_time)
                current_time += movement_penalty
            else:
                factory_start_time[j].append(-1)
                factory_finish_time[j].append(-1)
    #last element of movement_times is total construction time

    return factory_assignments, factory_start_time, factory_finish_time

if __name__ == "__main__":
   
    
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

    #bays = [(1,1), (999999, 999999),(500,500), (0,0), (0,0)]
    #facts = [(0, 0), (1000000, 1000000), (500,500)]
    n_factories = 2
    n_vehicles = 3
    n_locations = len(facts)
    factory_assignments, start_times, end_times=k_median_single_factory_moving(bays, facts, n_vehicles, n_factories)
    print(factory_assignments)
    print(start_times)
    print(end_times)

    #plot results
    plt.figure(figsize=(10,15))
    plt.scatter(*zip(*bays), marker='.', color='k', label='bays')
    plt.scatter(*zip(*facts), marker='x', color='k', label='factories')

    for j in range(n_factories):
        color=np.random.choice(range(256), size=3)/256
        k = 0
        for factory, assigned_bays in factory_assignments[j].items():
            k += 1
            if assigned_bays != []: #no bays assigned to factory
                c = color / n_locations * k
                i=list(factory_assignments[j].keys()).index(factory)
                plt.scatter(factory[0], factory[1], marker='o',s=70, color=c)
                plt.scatter(*zip(*assigned_bays), marker='.', color=c, label='bays assigned to factory '+str(factory)+' at time t='+str(start_times[j][i]))
    #plt.plot(*zip(*bbox), color='blue', label='bounding box for test')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()
    ttm=max(max(v) for k, v in end_times.items())
    plt.title('Total time: '+str(ttm) +'min')
    plt.show()
