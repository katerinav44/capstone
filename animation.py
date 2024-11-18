import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import numpy as np
from move_factory_multi_MIP_cluster import *
from run_factories import *
from run_factory import *

def animate_factories(bays, factory_assignments, start_times, end_times, n_factories, speed_up_factor=1000):
    """
    Create an animated visualization of factory movements.
    
    Parameters:
    - bays: List of bay coordinates.
    - factory_assignments: Factory assignments.
    - start_times: Start times for factory operation at each location.
    - end_times: End times for factory operation at each location.
    - n_factories: Number of factories.
    - speed_up_factor: Factor by which to scale down time.
    """
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(min(x for x, _ in bays), max(x for x, _ in bays))
    ax.set_ylim(min(y for _, y in bays), max(y for _, y in bays))
    
    # Plot all bays
    bay_scatter = ax.scatter(*zip(*bays), color='gray', s=5, label='Bays')
    
    # Initialize scatter plots for factories
    factory_scatter = [
        ax.scatter([], [], s=100, label=f'Factory {j + 1}') for j in range(n_factories)
    ]
    
    # Scale times and filter out -1 values
    scaled_start_times = {
        j: [t / speed_up_factor if t != -1 else np.inf for t in times]
        for j, times in start_times.items()
    }
    scaled_end_times = {
        j: [t / speed_up_factor if t != -1 else np.inf for t in times]
        for j, times in end_times.items()
    }
    
    # Calculate total animation time, excluding infinities
    total_time = max(
        max(t for t in times if t != np.inf) for times in scaled_end_times.values()
    )

    def init():
        """Initialize the animation."""
        for scatter in factory_scatter:
            scatter.set_offsets(np.array([]).reshape(0, 2))  # Empty scatter for each factory
        return factory_scatter

    def update(frame):
        """Update the positions of factories at each frame."""
        for j, scatter in enumerate(factory_scatter):
            active_locations = [
                loc for i, loc in enumerate(factory_assignments[j])
                if scaled_start_times[j][i] <= frame <= scaled_end_times[j][i]
            ]
            scatter.set_offsets(active_locations)
        return factory_scatter

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=range(int(total_time) + 1),
        init_func=init,
        blit=False,  # Disable blitting for backend compatibility
        repeat=False
    )

    ax.legend()
    plt.show()
    return ani


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
factory_assignments, start_times, end_times = multi_MIP(bays, facts, n_vehicles, n_factories)
print(end_times)
# Call the animation function with data
ani = animate_factories(bays, factory_assignments, start_times, end_times, n_factories)
