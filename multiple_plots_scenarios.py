import matplotlib.pyplot as plt
import numpy as np
from mip_strategy_generator import multi_MIP   # Import required functions
from run_factories import run_factories, estimate_cost  # Import the run_factories function
import json
from matplotlib.ticker import FormatStrFormatter


def format_time(ttm):
    """
    Format time as days depending on duration.
    """
    return ttm / 1440  # Convert to days (1440 minutes in a day)


def generate_factory_vehicle_plot(factory_data, factories, optimal_solution):
    """
    Create a plot for a specific number of factories, showing cost and time.
    Display the optimal solution in the plot title.
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

    ax2.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # No decimal points for cost
    ax1.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Two decimal points for time

    # Add data labels for the cost line
    for i, (x, y) in enumerate(zip(vehicles, costs)):
        ax2.text(x, y, f"{vehicles[i]} veh", fontsize=9, color='tab:green', ha='left', va='bottom')

    # Add optimal solution details to the title
    if optimal_solution:
        optimal_vehicle, optimal_cost, optimal_time = optimal_solution
        title = (
            f"Factory Count: {factories}\n"
            f"Optimal Solution: {factories} factories, {optimal_vehicle} vehicles, "
            f"Cost: ${optimal_cost:,.2f}, Time: {optimal_time:.2f} days"
        )
    else:
        title = f"Factory Count: {factories}"

    # Set title
    fig.suptitle(title, fontsize=14)
    fig.tight_layout()
    plt.show()



def generate_plots(bays, facts):
    """
    Generate plots for all factory and vehicle scenarios and include the optimal solution in the titles.
    """
    factories_range = range(1, 4)  # 1 to 3 factories
    vehicles_range = range(1, 10)  # 1 to 9 vehicles
    results = []

    # Collect data for individual factory plots
    factory_data = {factories: [] for factories in factories_range}
    optimal_solutions = {}

    for factories in factories_range:
        min_cost = float('inf')  # Initialize minimum cost
        optimal_vehicle = None
        optimal_time = None

        for vehicles in vehicles_range:
            # Run the multi_MIP function to get factory assignments
            factory_assignments, _, _, _ = multi_MIP(
                bays, facts, n_vehicles=vehicles, n_factories=factories, num_clusters=50
            )

            # Calculate ttm using the run_factories function
            ttm, _, _, _ = run_factories(factory_assignments, vehicles)

            # Estimate cost based on ttm
            cost = estimate_cost(ttm, vehicles, factories)
            time_in_days = format_time(ttm)
            results.append((factories, vehicles, cost, time_in_days))

            # Store data for factory-specific plots
            factory_data[factories].append((vehicles, cost, time_in_days))

            # Check for the optimal solution based on the lowest cost
            if cost < min_cost:
                min_cost = cost
                optimal_vehicle = vehicles
                optimal_time = time_in_days

        # Store the optimal solution for annotation
        optimal_solutions[factories] = (optimal_vehicle, min_cost, optimal_time)

    # Generate individual factory plots
    for factories, data in factory_data.items():
        generate_factory_vehicle_plot(data, factories, optimal_solutions.get(factories))



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

    generate_plots(bays, facts)
