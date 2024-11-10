import numpy as np
import scipy as sp
import scipy.spatial.distance as spd

def run_factory(fact, bays, vehicles, sort):
    t = 0
    buffer = []
    installed = []
    t_return = np.zeros(vehicles)
    t_built = []
    avail_cars = []
    
    if sort:
        bays = sort_by_dist(bays, fact)
    planned = list(bays)

    while installed != bays:
        for i in range(vehicles):
            if t == t_return[i]:
                avail_cars.append(i)
        
        if len(buffer) < 2 and len(planned) > 0:
            if len(buffer) == 1:
                if t >= t_built[0]:
                    build_bay = planned.pop(0)
                    t_built.append(build(build_bay, t))
                    buffer.append(build_bay)
            else:
                build_bay = planned.pop(0)
                t_built.append(build(build_bay, t))
                buffer.append(build_bay)
        
        if len(avail_cars) > 0 and len(buffer) > 0:
            if t >= t_built[0]:
                t_built.pop(0)
                deliver_bay = buffer.pop(0)
                installed.append(deliver_bay)
                car = avail_cars.pop(0)
                t_return[car] = deliver(fact, deliver_bay, t)

        t += 1

    t_finish = np.max(t_return)
    return t_finish

def build(bay, t):
    T_bay = 5
    t_built = t + T_bay
    return t_built

def deliver(fact, bay, t):
    v = 400
    T_install = 6
    distance = dist(fact, bay)
    travel = 2 * np.ceil(distance / v)
    t_return = t + travel + T_install
    return t_return

def dist(fact, bay):
    x_dist = np.abs(fact[0] - bay[0])
    y_dist = np.abs(fact[1] - bay[1])
    return x_dist + y_dist

def convert_text_coordinates(file_name):
    my_file = open(file_name, "r")
    data = my_file.read()
    str_list = data.split("\n") 
    my_file.close() 
    coordinates = []

    for entry in str_list:
        if len(entry) > 0:
            entry = entry.replace("'",'')
            entry = entry.replace("(",'')
            entry = entry.replace(")",'')
            entry = entry.replace(" ",'')
            entry = entry.split(",")
            x_coord = float(entry[0])
            y_coord = float(entry[1])
            coordinates.append((x_coord, y_coord))
    return coordinates

def sort_by_dist(coordinates, fact):
    coordinates.sort(key=lambda p: np.abs(p[0] - fact[0]) + np.abs(p[1] - fact[1]))
    return coordinates

# Modified function to find the ideal vehicle count based on a 5% improvement threshold
def test_vehicles_for_factories(max_vehicles, factories, bays, sort, improvement_threshold=0.10):
    for fact in factories:
        print(f"\nTesting for factory location: {fact}")
        previous_time = None
        ideal_vehicle_count = 1

        for i in range(1, max_vehicles + 1):
            total_time = run_factory(fact, bays, i, sort)
            print(f"  Vehicles: {i}, Total time: {total_time}")

            # Check if there's a previous time to compare with
            if previous_time is not None:
                improvement = (previous_time - total_time) / previous_time
                print(f"    Improvement from previous: {improvement:.2%}")

                # Check if improvement is less than the threshold
                if improvement < improvement_threshold:
                    ideal_vehicle_count = i - 1
                    print(f"    Ideal vehicle count for factory at {fact}: {ideal_vehicle_count}")
                    break

            previous_time = total_time

        # If we reach max_vehicles without meeting threshold, set ideal to max_vehicles
        if ideal_vehicle_count == 1:
            ideal_vehicle_count = max_vehicles
            print(f"    Ideal vehicle count for factory at {fact} (max reached): {ideal_vehicle_count}")

if __name__ == "__main__":
    max_vehicles = 10
    bays = convert_text_coordinates("panel_coordinates.txt")
    sort = True

    # List of factory locations
    factories = [(900, 6600), (3600, 0), (8100, 0), (8100, 3600)]

    # Run tests for each factory location
    test_vehicles_for_factories(max_vehicles, factories, bays, sort)
