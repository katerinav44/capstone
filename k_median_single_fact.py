from run_factory import run_factory, build, deliver, dist, convert_text_coordinates
import pulp as pl
import numpy as np
import scipy as sp
import scipy.spatial.distance as spd

# === Parameters ===
# Inputs
bays_list = convert_text_coordinates("panel_coordinates.txt")
bays = np.array(bays_list)
facts_list = [(900,6600),(3600,0),(8100,0),(8100,3600), (6300,2700), (11700,0)]
facts = np.array(facts_list)
n_bays = len(bays)
n_facts = len(facts)
# === Decision Variables ===

problem = pl.LpProblem("k_median", pl.LpMinimize)

# Coordinates of a factory (continuous variable)
X = pl.LpVariable.dicts("bay_factory", indices = (range(len(bays)), range(len(facts))), lowBound=0, upBound=1, cat='Binary')
Y = pl.LpVariable.dicts("factory_chosen", indices = range(len(facts)), lowBound=0, upBound=1, cat='Binary')

# === Objective Function ===
# Minimize k-median distance as a heuristic for time
problem += (
    sum(sum(spd.cityblock(bays[i], facts[j]) * X[i][j] for j in range(n_facts)) for i in range(n_bays))
), "k_median"

# === Constraints ===
k = 1
for i in range(n_bays):
    problem += sum(X[i][j] for j in range(n_facts)) == 1 # each bay i serviced by 1 factory

problem += sum(Y[j] for j in range(n_facts)) == k # k = 1 factories chosen total - expand to k = 1

for j in range(n_facts):
    problem += sum(X[i][j] for i in range(n_bays)) <= Y[j] * n_bays # each factory j services less than all bays

# === Solve the problem ===
problem.solve()

# === Output the results ===
print(f"Status: {pl.LpStatus[problem.status]}")
for j in range(n_facts):
    fact_time = run_factory(facts_list[j], bays_list, 2)
    fact_dist = sum(spd.cityblock(bays[i], facts[j]) for i in range(n_bays))
    print(f"Factory: {facts[j]}, Time: {fact_time}, Total Distance: {fact_dist}")
    if Y[j].varValue == 1:
        print(f"Factory Chosen: {facts[j]}")
