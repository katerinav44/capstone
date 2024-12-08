import matplotlib.pyplot as plt
import numpy as np
from move_factory_multi_MIP_cluster import multi_MIP, estimate_cost  # Import required functions
from run_factories import run_factories  # Import the run_factories function
import json
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter


def format_time(ttm):
    """
    Format time as days depending on duration.
    """
    if ttm > 10080:  # More than a week
        return ttm / 1440  # Convert to days (1440 minutes in a day)
    else:
        return ttm / 1440  # Always display in days

def generate_plot(bays, facts):
    """
    Generate a plot of cost vs. time to complete using multi_MIP and run_factories.
    """
    factories_range = range(1, 4)  # 1 to 3 factories
    vehicles_range = range(1, 10)  # 1 to 9 vehicles
    results = []

    # Define base colors for factories
    base_colors = plt.get_cmap("tab10").colors

    for factories in factories_range:
        for vehicles in vehicles_range:
            # Run the multi_MIP function to get factory assignments
            factory_assignments, _, _, _ = multi_MIP(
                bays, facts, n_vehicles=vehicles, n_factories=factories, num_clusters=50
            )
            
            # Calculate ttm using the run_factories function
            ttm, _, _, _ = run_factories(factory_assignments, vehicles)

            # Estimate cost based on ttm
            cost = estimate_cost(ttm, vehicles, factories)  
            results.append((factories, vehicles, cost, format_time(ttm)))
            print(results)
    # Extract data for plotting
    x_data = [r[2] for r in results]  # Cost
    y_data = [r[3] for r in results]  # Time in days
    

    labels = [(r[0], r[1]) for r in results]  # Factories and vehicles

    # Plot the results
    plt.figure(figsize=(12, 8))
    ax = plt.gca()  # Get the current axis

    x_offset = 0.01 * (max(x_data) - min(x_data))  # Adjust offset relative to x-axis range

    for factories in factories_range:
        # Assign a single color to each factory configuration
        factory_color = base_colors[(factories - 1) % len(base_colors)]

        for vehicles in vehicles_range:
            idx = (factories - 1) * len(vehicles_range) + (vehicles - 1)
            label_text = f"{vehicles}"

            # Only add legend entry for the first vehicle of each factory configuration
            plt.scatter(
                x_data[idx],
                y_data[idx],
                color=factory_color,
                label=f"{factories} factory" if vehicles == 1 else None,
                alpha=0.8,
            )

            # Alternate label position based on factory number
            if factories % 2 == 0:  # Even factories: left side
                plt.annotate(
                    label_text,
                    (x_data[idx] - x_offset, y_data[idx]),
                    fontsize=8,
                    ha="right",  # Align text to the right
                    alpha=0.7,
                )
            else:  # Odd factories: right side
                plt.annotate(
                    label_text,
                    (x_data[idx] + x_offset, y_data[idx]),
                    fontsize=8,
                    ha="left",  # Align text to the left
                    alpha=0.7,
                )

    plt.title('Cost vs Time to Complete for Various Factory and Vehicle Configurations')
    plt.xlabel('Cost Estimate (USD)')
    plt.ylabel('Time to Complete (days)')
    plt.grid(True)

        # Disable scientific notation on both axes
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.0f'))  # No decimal points for cost
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))  # Two decimal points for time


    # Avoid duplicate legends
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize=8)

    plt.show()

    # Print summary of times and costs for each scenario
    print("\nSummary of Times and Costs for Each Scenario:")
    for result in results:
        factories, vehicles, cost, ttm_in_days = result
        print(f"{factories} factories, {vehicles} vehicles: {ttm_in_days:.2f} days, Cost: ${cost:,.2f}")


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
    generate_plot(bays, facts)
