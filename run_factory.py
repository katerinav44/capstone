import numpy as np
import scipy as sp
import scipy.spatial.distance as spd

def run_factory(fact, bays, vehicles):
    t = 0
    buffer = []
    installed = []
    t_return = np.zeros(vehicles)
    t_built = []
    avail_cars = []
    
    #print(fact)
    planned = list(bays)

    while installed != bays:
        for i in range(vehicles):
            # car has returned from delivery + install
            if t == t_return[i]:
                avail_cars.append(i)
        
        # building a new bay
        if len(buffer) < 2 and len(planned) > 0:
            build_bay = planned.pop(0)
            t_built.append(build(build_bay, t))
            buffer.append(build_bay)
        
        # delivering and installing a built bay
        if len(avail_cars) > 0 and len(buffer) > 0:
            if t >= t_built[0]:
                t_built.pop(0)
                deliver_bay = buffer.pop(0)
                installed.append(deliver_bay)
                car = avail_cars.pop(0)
                t_return[car] = deliver(fact, deliver_bay, t)
        # print("t = %i" %t)
        # print("Planned: {}".format(planned))
        # print("Built: {}".format(t_built))
        # print("Buffer: {}".format(buffer))
        # print("Installed: {}".format(installed))
        # print("Available Cars: {}".format(avail_cars))
        # print("Return Cars: {}".format(t_return))

        t += 1
    t_finish = np.max(t_return)
    #print("Finish Building at t = %i" %t_finish)
    return t_finish

def build(bay, t):
    T_bay = 5 # 4-5 min to assembly
    t_built = t + T_bay
    return t_built

def deliver(fact, bay, t):
    v = 400 # 24 km/h = 400 m/min
    T_install = 6 # 6 min to install

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
            coordinates.append(tuple([x_coord, y_coord]))
    return coordinates

def sort_by_dist(coordinates, fact):
    coordinates.sort(key = lambda p: np.abs(p[0] - fact[0]) + np.abs(p[1] - fact[1]))
    return coordinates
# testing reducing build time with different more vehicles
def test_vehicles(max_vehicles, fact, bays):
    for i in range(1,max_vehicles):
        print("Vehicles: %i" %i)
        run_factory(fact, bays, i)

# testing reducing build time with different factory locations
def test_factories(vehicles, facts, bays):
    for fact in facts:
        print("Factory: {}".format(fact))
        run_factory(fact, bays, vehicles)

# testing reducing build time by sorting bays by distance
def test_sort(vehicles, fact, bays):
    sort = False
    print("Sort = {}".format(sort))
    run_factory(fact, bays, vehicles, sort)

    sort = True
    bays = sort_by_dist(bays, fact)
    print("Sort = {}".format(sort))
    run_factory(fact, bays, vehicles)

max_vehicles = 5
fact = (0,0)
bays = convert_text_coordinates("panel_coordinates.txt")
sort = False
#test_vehicles(max_vehicles, fact, bays, sort)

vehicles = 3
facts = [(900,6600),(3600,0),(8100,0),(8100,3600)]
#test_factories(vehicles, facts, bays)

fact = facts[0]
#test_sort(vehicles, fact, bays)