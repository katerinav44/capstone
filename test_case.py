from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import json
from run_factories_no_move import *

# Define Regions
green_rectangles = [
    Polygon([(-130, 1900), (1000, 1900), (1000, 1290), (-130, 1290)]),  # Rectangle 1
    Polygon([(-130, 1300), (280, 1300), (280, 1160), (-130, 1160)]),  # Rectangle 2
    Polygon([(-130, 1170), (200, 1170), (200, 1080), (-130, 1080)])   # Rectangle 3
]

blue_rectangle = Polygon([(620, 240), (620, 1250), (1200, 1250), (1200, 240)])

circled_factories = [
    (342, 1424),  # green factory coordinates
    (305, 817),   # orange factory coordinates
    (967, 855)    # blue factory coordinates
]

    # Load Data from JSON File
with open('test_data_20k.json', 'r') as file:
   data = json.load(file)

bays = [(bay['x'], bay['y']) for bay in data['bays']]

# Assign Panels to Factories Based on Rectangles
factory_assignments = {"green": [], "blue": [], "orange": []}

# Pre-allocate the lists for each region
green_coords = []
blue_coords = []
orange_coords = []

# Assign each bay to the appropriate region
for coord in bays:
    point = Point(coord)
        
    # Check if the point falls within any green rectangle
    if any(rect.contains(point) for rect in green_rectangles):
        green_coords.append(coord)
    elif blue_rectangle.contains(point):
        blue_coords.append(coord)
    else:
        orange_coords.append(coord)

if __name__ == "__main__":
    # Open a file to write output
    with open("test_case_time.txt", "w") as file:
        # Redirect standard output to the file
        original_stdout = sys.stdout  # Save the original standard output
        sys.stdout = file  # Change standard output to the file

        # Define the factory assignments as before
        factory_assignments = {0: {(305, 817): blue_coords},
                            1: {(342, 1424): green_coords},
                            2: {(967, 855): orange_coords}} 
        
        # Run the simulation with this configuration
        run_factories(factory_assignments, 3)

        # Reset standard output back to original
        sys.stdout = original_stdout