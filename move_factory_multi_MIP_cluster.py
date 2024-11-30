import pulp as pl
from pulp import LpProblem, LpMinimize, PULP_CBC_CMD, GUROBI
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from sklearn.cluster import KMeans
from run_factory import *
from run_factories import *
from scipy.spatial import distance

def cluster_bays(bays, num_clusters=1000):
    # Convert bay locations to a numpy array if they aren’t already
    bays_array = np.array(bays)
    
    # Perform clustering
    kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(bays_array)
    
    # Get cluster centroids, which will serve as representative locations for grouped bays
    cluster_centers = kmeans.cluster_centers_
    # Count the number of bays in each cluster
    bay_weights = np.bincount(kmeans.labels_)
    
    return cluster_centers, bay_weights, kmeans.labels_


def multi_MIP(bays, facts, n_vehicles, n_factories, num_clusters=50):
    # Cluster bay locations to reduce problem size
    cluster_centers, bay_weights, labels = cluster_bays(bays, num_clusters=num_clusters)
    facts_L = facts
    cluster_centers = np.array(cluster_centers)
    facts = np.array(facts)
    n_clusters = len(cluster_centers)
    n_locations = len(facts)

    problem = pl.LpProblem("k_median_moving_factory", pl.LpMinimize)
    
    # === Decision Variables ===
    X = pl.LpVariable.dicts("service_bay", indices=(range(n_clusters), range(n_factories), range(n_locations)), lowBound=0, upBound=1, cat='Binary')
    Y = pl.LpVariable.dicts("move_factory", indices=(range(n_factories), range(n_locations)), lowBound=0, upBound=1, cat='Binary')
    max_time = pl.LpVariable('max_time', lowBound=0, cat='Continuous')

    # === Objective Function ===
    movement_penalty = 60 * 24
    problem += max_time  # Objective function to minimize

    # Add terms to the objective function, weighted by the number of bays in each cluster
    for j in range(n_factories):
        problem += (sum(Y[j][k] for k in range(n_locations)) - 1) * movement_penalty + \
                   sum(run_factory(facts[k], [cluster_centers[i]], n_vehicles, True) * X[i][j][k] * bay_weights[i]
                       for k in range(n_locations) for i in range(n_clusters)) <= max_time

    # === Constraints ===
    # Each cluster is serviced by exactly one factory
    for i in range(n_clusters):
        problem += sum(X[i][j][k] for k in range(n_locations) for j in range(n_factories)) == 1

    # Each location can be served by at most one factory
    for k in range(n_locations):
        problem += sum(Y[j][k] for j in range(n_factories)) <= 1

    # A factory can only service a bay cluster if it's active at the location
    for i in range(n_clusters):
        for j in range(n_factories):
            for k in range(n_locations):
                problem += X[i][j][k] <= Y[j][k]

    # === Solve the problem ===
    problem.solve(solver=PULP_CBC_CMD(msg=True, timeLimit=120*5))

    # === Output the results ===
    print(f"Status: {pl.LpStatus[problem.status]}")
    print(f"Objective Value: {pl.value(problem.objective)}")

    # Map clusters to the factories they are assigned to
    cluster_assignments = {j: {tuple(loc): [] for loc in facts_L} for j in range(n_factories)}
    x = np.zeros((n_clusters, n_factories, n_locations))
    y = np.zeros((n_factories, n_locations))
    
    for k in range(n_locations):
        for j in range(n_factories):
            if Y[j][k].varValue == 1:
                y[j][k] = 1
            for i in range(n_clusters):
                if X[i][j][k].varValue == 1:
                    x[i][j][k] = 1
                    cluster_assignments[j][tuple(facts_L[k])].append(tuple(cluster_centers[i]))

    # === Unclustered Bay Assignments ===
    # Assign each original bay to the nearest active factory based on the cluster assignments
    factory_assignments = {j: {tuple(loc): [] for loc in facts_L} for j in range(n_factories)}
    for j in range(n_factories):
      for k, location in enumerate(facts_L):
        if y[j][k] == 1:  # If factory j is active at location k
            assigned_bays = [tuple(bays[i]) for i in range(len(bays)) if labels[i] in [
                idx for idx, assigned_clusters in enumerate(cluster_centers) if tuple(assigned_clusters) in cluster_assignments[j][tuple(location)]
            ]]
            factory_assignments[j][tuple(location)].extend(assigned_bays)

    # === Compute construction and movement times  ===
    t_finish, factory_start_time, factory_finish_time, cost=run_factories(factory_assignments, n_vehicles)
    print(factory_start_time, factory_finish_time)
    # factory_start_time = {}
    # factory_finish_time = {}

    # for j in range(n_factories):
    #     current_time = 0
    #     factory_start_time[j] = []
    #     factory_finish_time[j] = []
    #     for k in range(n_locations):
    #         if factory_assignments[j][tuple(facts_L[k])]:
    #             factory_start_time[j].append(current_time)
    #             current_time += run_factory(facts_L[k], factory_assignments[j][facts_L[k]], n_vehicles, True)
    #             factory_finish_time[j].append(current_time)
    #             current_time += movement_penalty
    #         else:
    #             factory_start_time[j].append(-1)  # No bays assigned to the factory
    #             factory_finish_time[j].append(-1)

    return factory_assignments, factory_start_time, factory_finish_time, cost

if __name__ == "__main__":
    with open('test_data_20k.json', 'r') as file:
        data = json.load(file)

    bays = []
    facts = []
    for i in range(len(data['bays'])):
        bays.append((data['bays'][i]['x'], data['bays'][i]['y']))

    for i in range(len(data['factory_locations'])):
        facts.append((data['factory_locations'][i]['x'], data['factory_locations'][i]['y']))

    # Bounding box to test on a subset of bays
    xmin, xmax, ymin, ymax = 700, 1100, 1000, 1750
    bays_test1 = []
    for i in range(len(bays)):
        x = bays[i][0]
        y = bays[i][1]
        if xmin <= x <= xmax and ymin <= y <= ymax:
            bays_test1.append((x, y))

    n_factories = 3
    n_vehicles = 3
    n_locations = len(facts)
    print(n_locations)
    factory_assignments, start_times, end_times, cost = multi_MIP(bays, facts, n_vehicles, n_factories)

    # Define one color for each factory
    color_palette = plt.get_cmap('Set1')
    factory_colors = [color_palette(i % 10) for i in range(n_factories)]  # Cycle if n_factories > 10

    # Plot results
    plt.figure(figsize=(10, 10))

    def generate_distinct_shades(base_color, num_shades): 
        h, l, s = mcolors.rgb_to_hsv(base_color[:3])  # Convert to HSV 
        shades = []
        for i in range(num_shades):
            # Adjust hue, lightness and saturation 
            new_h = (h + 0.025* (i - num_shades // 2)) % 1.0 
            new_l = max(0, min(l - 0.1 * (i - num_shades // 2), 1.0))  # Increase or dec lightness
            new_s = max(0, min(s - 0.03 * (i - num_shades // 2), 1.0))  # Slightly saturate
            shades.append(mcolors.hsv_to_rgb((new_h, new_l, new_s)))
        return shades
    
    # Plot each bay and factory with consistent coloring per factory
    for j in range(n_factories):
        color = factory_colors[j]  #color for each factory
        shades = generate_distinct_shades(color, len(factory_assignments[j]))
    
        for i, (factory, assigned_bays) in enumerate(factory_assignments[j].items()):
            if assigned_bays:  # Only plot if there are bays assigned to the factory at this location
                color = shades[i]
                plt.scatter(factory[0], factory[1], marker='o', s=70, color=color)
            
                # Plot the bays assigned to this factory
                plt.scatter(*zip(*assigned_bays), marker='.', color=color,  
                        label=f'bays assigned to factory {factory} at t={start_times[j][i]}')

    # Plot bounding box 
    # plt.plot(*zip(*bbox), color='blue', label='bounding box for test')
    print(facts)
    # Set plot labels and title
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend(loc='lower left')
    ttm = max(max(v) for v in end_times.values())
    plt.suptitle(f'Total build time: {ttm} min. Cost: ${cost:.2f}.',x=0.53)
    plt.title(f'Number of factories: {n_factories}. Number of vehicles: {n_vehicles*n_factories}')
    plt.tight_layout()
    plt.show()
    