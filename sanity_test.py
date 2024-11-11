import numpy as np
from run_factory import run_factory
from run_factory import test_factories
# 5 set of sanity tests

# Case 1: 1 Vehicles, 1 Factory, 3 Panels
# [Calculated Time: Location 1 - 35 min, Location 2 - 29 min, Location 3 - 35 min]
bays = [(500, 100), (500, 200), (500, 300)]
factories = [(0, 0), (200, 200), (100, 400)]
vehicles = 1
sort = False
# Run test to determine the best factory location
print("\nTesting Out Case 1 (3 panels, 1 vehicle):")
test_factories(vehicles, factories, bays, sort)


# Case 2: 2 Vehicles, 1 Factory, 3 Panels
# [Calculated Time: Location 1 - 25 min, Location 2 - 23 min, Location 3 - 25 min]
bays = [(500, 100), (500, 200), (500, 300)]
factories = [(0, 0), (200, 200), (100, 400)]
vehicles = 2
sort = False
# Run test to determine the best factory location
print("\nTesting Case 2 (3 panels, 2 vehicles):")
test_factories(vehicles, factories, bays, sort)


# Case 3: 1 Vehicles, 1 Factory, 6 Panels (2 rows)
# [Calculated Time: Location 1 - 67 min, Location 2 - 57 min, Location 3 - 65 min]
bays = [(500, 100), (600, 100), (500, 200), (600, 200), (500, 300), (600, 300)]
factories = [(0, 0), (200, 200), (100, 400)]
vehicles = 1
sort = False
# Run test to determine the best factory location
print("\nTesting Case 3 (6 panels, 1 vehicle):")
test_factories(vehicles, factories, bays, sort)


# Case 4: 2 Vehicles, 1 Factory, 6 Panels (2 rows)
# [Calculated Time: Location 1 - 42 min, Location 2 - 40 min, Location 3 - 40 min]
bays = [(500, 100), (600, 100), (500, 200), (600, 200), (500, 300), (600, 300)]
factories = [(0, 0), (200, 200), (100, 400)]
vehicles = 2
sort = False
# Run test to determine the best factory location
print("\nTesting Out Case 3 (6 panels, 2 vehicles):")
test_factories(vehicles, factories, bays, sort)


# Case 5: Moving factories
# [Calculated Time: Location 1 - 35 min, Location 2 - 29 min, Location 3 - 35 min]
bays = [(500, 100), (600, 100), (500, 200), (600, 200), (500, 300), (600, 300)]
factories = [(0, 0), (200, 200), (100, 400)]
vehicles = 2
sort = True
# Run test to determine the best factory location
print("\nTesting Out Case 5 (moving factories):")
test_factories(vehicles, factories, bays, sort)