import matplotlib.pyplot as plt
import numpy as np
from move_factory_multi_MIP_cluster import multi_MIP, estimate_cost  # Import required functions
from run_factories import run_factories  # Import the run_factories function
import json
import matplotlib.colors as mcolors
import random

def format_time(ttm):
    """
    Format time as days depending on duration.
    """
    return ttm / 1440  # Convert to days (1440 minutes in a day)

def generate_factory_vehicle_plot(factory_data, factories):
    """
    Create a separate plot for a specific number of factories,
    showing cost on the right y-axis, time (in days) on the left y-axis,
    and number of vehicles on the x-axis.
    Add data labels for the number of vehicles on both time and cost lines.
    """
    vehicles = [data[0] for data in factory_data]  # Number of vehicles
    costs = [data[1] for data in factory_data]  # Costs
    times = [data[2] for data in factory_data]  # Time in days

    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot time on the left y-axis
    ax1.set_xlabel('Number of Vehicles')
    ax1.set_ylabel('Time to Complete (days)', color='tab:blue')
    ax1.plot(vehicles, times, marker='o', color='tab:blue', label='Time (days)')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Add data labels for the time line
    for i, (x, y) in enumerate(zip(vehicles, times)):
        ax1.text(x, y, f"{vehicles[i]} veh", fontsize=9, color='tab:blue', ha='left', va='bottom')

    # Plot cost on the right y-axis
    ax2 = ax1.twinx()
    ax2.set_ylabel('Cost Estimate (USD)', color='tab:green')
    ax2.plot(vehicles, costs, marker='o', linestyle='--', color='tab:green', label='Cost (USD)')
    ax2.tick_params(axis='y', labelcolor='tab:green')

    # Add data labels for the cost line
    for i, (x, y) in enumerate(zip(vehicles, costs)):
        ax2.text(x, y, f"{vehicles[i]} veh", fontsize=9, color='tab:green', ha='left', va='bottom')

    # Title and legend
    fig.suptitle(f'Factory Count: {factories}', fontsize=14)
    fig.tight_layout()
    plt.show()

def generate_plots(bays, facts):
    """
    Generate the main plot and individual factory-vehicle plots.
    """
    factories_range = range(1, 4)  # 1 to 3 factories
    vehicles_range = range(1, 5)  # 1 to 4 vehicles
    results = []

    # Collect data for individual factory plots
    factory_data = {factories: [] for factories in factories_range}

    for factories in factories_range:
        for vehicles in vehicles_range:
            # Run the multi_MIP function to get factory assignments
            factory_assignments, _, _, _ = multi_MIP(
                bays, facts, n_vehicles=vehicles, n_factories=factories, num_clusters=50
            )
            
            # Calculate ttm using the run_factories function
            ttm, _, _, _ = run_factories(factory_assignments, vehicles)

            # Estimate cost based on ttm
            cost = estimate_cost(vehicles, factories, ttm / 60)  # Convert ttm to hours
            time_in_days = format_time(ttm)
            results.append((factories, vehicles, cost, time_in_days))

            # Store data for factory-specific plots
            factory_data[factories].append((vehicles, cost, time_in_days))

    # Generate individual factory plots
    for factories, data in factory_data.items():
        generate_factory_vehicle_plot(data, factories)
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

    n_factories = 2
    n_vehicles = 3
    n_locations = len(facts)
    print(n_locations)
    generate_plots(bays, facts)
