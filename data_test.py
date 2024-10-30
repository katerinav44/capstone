from run_factory import *
from k_median_single_fact import *
import json
import matplotlib.pyplot as plt
import numpy as np

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

t_finish_test1=test_factories(100, facts, bays_test1, True)
#get index of min time factory
#index_min = np.argmin(t_finish_test1)
min_value = min(t_finish_test1)
min_fact_test1=[facts[i] for i, x in enumerate(t_finish_test1) if x == min_value]

n_vehicles=10
min_fact_test2=k_median_single_factory(bays_test1, facts, n_vehicles)

#plot bays and factories 
plt.figure(figsize=(10,15))
plt.scatter(*zip(*bays), marker='.', color='k', label='bays')
plt.scatter(*zip(*facts), marker='x', color='red', label='factories')
plt.scatter(*zip(*min_fact_test2), marker='o', s=70,color='green', label='optimal factory location')
plt.plot(*zip(*bbox), color='blue', label='bounding box for test')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.show()
