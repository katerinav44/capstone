from run_factory import run_factory, build, deliver, dist, convert_text_coordinates
import pulp as pl
import numpy as np
import scipy as sp
import json
import scipy.spatial.distance as spd

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
xmax=250
ymin=750
ymax=1000
bbox=[(xmin,ymin), (xmax,ymin), (xmax,ymax), (xmin,ymax), (xmin,ymin)]
#remove bays not in the box
bays_test1=[]
for i in range(len(bays)):
    x=bays[i][0]
    y=bays[i][1]
    if x>=xmin and x<=xmax and y>=ymin and y<=ymax:
        bays_test1.append((x,y))


# === Decision Variables ===

def k_median_single_factory(bays, facts, n_vehicles, k):
    bays_list=bays
    facts_list=facts
    bays = np.array(bays_list)
    facts = np.array(facts_list) #the most annoying way of doing this I know
    n_bays = len(bays)
    n_facts = len(facts) # we should also account for the fact that there may be less factories than available factory locations
    problem = pl.LpProblem("k_median", pl.LpMinimize)

    # X and Y decision variables
    X = pl.LpVariable.dicts("bay_factory", indices = (range(len(bays)), range(len(facts))), lowBound=0, upBound=1, cat='Binary')
    Y = pl.LpVariable.dicts("factory_chosen", indices = range(len(facts)), lowBound=0, upBound=1, cat='Binary')

    # === Objective Function ===
    # Minimize k-median distance as a heuristic for time
    problem += (
        sum(sum(spd.cityblock(bays[i], facts[j]) * X[i][j] for j in range(n_facts)) for i in range(n_bays))
    ), "k_median"

    # === Constraints ===
    for i in range(n_bays):
        problem += sum(X[i][j] for j in range(n_facts)) == 1 # each bay i serviced by 1 factory

    problem += sum(Y[j] for j in range(n_facts)) == k # k = 1 factories chosen total - expand to k = 1

    for j in range(n_facts):
        problem += sum(X[i][j] for i in range(n_bays)) <= Y[j] * n_bays # each factory j services less than all bays

    # === Solve the problem ===
    problem.solve()

    # === Output the results ===
    print(f"Status: {pl.LpStatus[problem.status]}")
    optimal_facts=[]
    for j in range(n_facts):
        fact_time = run_factory(facts_list[j], bays_list, n_vehicles, True)
        fact_dist = sum(spd.cityblock(bays[i], facts[j]) for i in range(n_bays))
        print(f"Factory: {facts[j]}, Time: {fact_time}, Total Distance: {fact_dist}")
        if Y[j].varValue == 1:
            print(f"Factory Chosen: {facts[j]}")
            optimal_facts.append(facts[j])
    return optimal_facts


#k_median_single_factory(bays_test1, facts, 2, 3)