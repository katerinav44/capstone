import itertools
import math
import numpy as np
from run_factory import *
import json
import matplotlib.pyplot as plt



def calculate_time(factory_locations, bays):
    total_time = 0
    factory_assignments = {factory: [] for factory in factory_locations}

    # Assign each bay to the closest factory
    for bay in bays:
        closest_factory = min(factory_locations, key=lambda factory: dist(factory, bay))
        factory_assignments[closest_factory].append(bay)
    
    constr_times=[]

    for factory, assigned_bays in factory_assignments.items():
        if list(factory_assignments).index(factory) ==0:
            #first factory means no movement
            constr_times.append(run_factory(factory, assigned_bays, 1, True))
        else:
            move_penalty=60*24 #1 day
            # changed to 1 vehicle - 3 vehicles localized = 1 vehicle per factory
            constr_times.append(run_factory(factory, assigned_bays, 1, True)+ move_penalty)
    
    return sum(constr_times), constr_times, factory_assignments

def heuristic_solution(bays, factory_locations, n_factories):
    best_time = float('inf')
    best_assignment = None

    # Generate all combinations of two factory locations
    for i in range (1,n_factories):
        for factory_group in itertools.combinations(factory_locations, i):
            time, times, assignments = calculate_time(factory_group, bays)
            if time < best_time:
                best_time = time
                best_movement_times = times
                best_assignment = factory_group
                best_assignments_dict=assignments

    print("Best Factory Locations:", best_assignment)
    print("Total Time Required:", best_time)
    print("Factory movement times:", best_movement_times)
    #print("Assignments", best_assignments_dict)

    return best_assignment, best_time, best_movement_times, best_assignments_dict



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


best_assignment, best_time, best_movement_times, best_assignments_dict=heuristic_solution(bays_test1, facts, len(facts))

plt.figure(figsize=(10,15))
plt.scatter(*zip(*bays), marker='.', color='k', label='bays')
plt.scatter(*zip(*facts), marker='x', color='k', label='factories')


for factory, assigned_bays in best_assignments_dict.items():
    i= list(best_assignments_dict).index(factory)
    color=np.random.choice(range(256), size=3)/256
    plt.scatter(factory[0], factory[1], marker='o',s=70, color=color)
    plt.scatter(*zip(*assigned_bays), marker='.', color=color, label='bays assigned to factory '+str(factory)+' at time: '+str(best_movement_times[i]))


plt.plot(*zip(*bbox), color='blue', label='bounding box for test')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.title('Total time: '+str(best_time))
plt.show()



