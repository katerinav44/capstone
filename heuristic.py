import itertools
import math
import numpy as np
from run_factory import *
import json


def calculate_time(factory_locations, bays):
    total_time = 0
    factory_assignments = {factory: [] for factory in factory_locations}

    # Assign each bay to the closest factory
    for bay in bays:
        closest_factory = min(factory_locations, key=lambda factory: dist(factory, bay))
        factory_assignments[closest_factory].append(bay)
    
    constr_times=[]
    for factory, assigned_bays in factory_assignments.items():
        # changed to 1 vehicle - 3 vehicles localized = 1 vehicle per factory
        constr_times.append(run_factory(factory, assigned_bays, 1, True))
    #Since the factories are building at the same time, the time it would take to build the whole site corresponds to the maximum time among each construction group
    return max(constr_times), factory_assignments

def heuristic_solution(bays, factory_locations, n_factories):
    best_time = float('inf')
    best_assignment = None

    # Generate all combinations of two factory locations
    for factory_group in itertools.combinations(factory_locations, n_factories):
        time, assignments = calculate_time(factory_group, bays)
        if time < best_time:
            best_time = time
            best_assignment = factory_group
            best_assignments_dict=assignments

    print("Best Factory Locations:", best_assignment)
    print("Total Time Required:", best_time)
    #print("Assignments", best_assignments_dict)

    return best_assignment, best_time, best_assignments_dict




