import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.colors as mcolors
import numpy as np
from mip_strategy_generator import *
from run_factories import *
from run_factory import *

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import ListedColormap
from matplotlib import colormaps

def animate_factories(bays_timeline, factory_timeline, factory_assignments):

    bay_to_factory = {}
    for fact, coords in factory_assignments.items():
        for coord, bays in coords.items():
            for bay in bays:
                bay_to_factory[bay] = fact

    fig, ax = plt.subplots()

    # Set up the scatter plot
    bay_scatter = ax.scatter([], [],marker='.', c='gray', label='Bays')
    factory_scatter = ax.scatter([], [], c='black', label='Factories')

    ax.legend()
    ax.set_xlim(0, 1250)  # Adjust limits as per your data
    ax.set_ylim(0, 2000)
    ax.set_title('Site construction with 2 factories and 6 vehicles')

    # Define a custom colormap
    factory_colormap = colormaps['Set2']  # Black for inactive, red for active

    def init():
        # Initialize empty 2D arrays for scatter data
        bay_scatter.set_offsets(np.empty((0, 2)))
        factory_scatter.set_offsets(np.empty((0, 2)))
        factory_scatter.set_array(np.array([]))  # Clear previous colors
        return factory_scatter, bay_scatter

    def update(frame):
        # Extract bays that are active up to the current frame
        active_bays = [coords for time, coords in bays_timeline if time <= frame]
        bay_colors = [bay_to_factory[bay]/(len(factory_assignments) - 1) for bay in active_bays]

        # Determine active factories based on start and end times
        active_factories = []
        factory_colors = []
        for coords, start_time, end_time in factory_timeline:
            if start_time <= frame <=end_time:
                active_factories.append(coords)
                for fact in factory_assignments.keys():
                    if factory_assignments[fact][coords]:
                        factory_colors.append(fact/(len(factory_assignments) - 1))

        # Update scatter data for bays
        bay_scatter.set_offsets(np.array(active_bays) if len(active_bays) else np.empty((0, 2)))
        bay_scatter.set_array(np.array(bay_colors))
        
        # Update factory positions and their color
        factory_scatter.set_offsets(np.array(active_factories) if len(active_factories) else np.empty((0,2)))
        factory_scatter.set_array(np.array(factory_colors))  # Update factory colors with numeric values
        
        # Set the colormap
        factory_scatter.set_cmap(factory_colormap)
        bay_scatter.set_cmap(factory_colormap)
        
        return factory_scatter, bay_scatter

    # Determine total frames based on timeline and skip frames for speed
    total_frames = int(max(t for t, _ in bays_timeline) + 1)
    skip_rate = 500 # Adjust this to skip more frames
    frames = range(0, total_frames, skip_rate)
    
    # Set up the animation with higher speed
    anim = animation.FuncAnimation(
        fig, update, frames=frames, init_func=init, blit=False, interval=50  # interval in milliseconds
    )
    # Save the animation as a GIF using PillowWriter
    writer = PillowWriter(fps=1000)  # Frames per second
    plt.show()
    anim.save("factory_animation.gif", writer=writer)


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
factory_assignments, start_times, end_times, bay_timeline = multi_MIP(bays, facts, n_vehicles, n_factories)
print(start_times)
# Call the animation function with data
factory_timeline = [
    (factory_position, start_time, end_time)
    for factory in range(n_factories)
    for factory_position, start_time, end_time
    in zip(facts, start_times[factory], end_times[factory])
    if start_time != -1  # Ignore locations where no work was done
]
print(factory_timeline)
ani = animate_factories(bay_timeline, factory_timeline, factory_assignments)
