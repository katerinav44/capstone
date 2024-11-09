import numpy as np
import scipy as sp
import scipy.spatial.distance as spd

def run_factory_float(facts, fact_bay, vehicles):
    # facts: list of factory locations, used to index fact_bay
    # fact_bay: dictionary of bays assigned to factories
    t = 0
    buffer = {factory: [] for factory in facts}
    planned = fact_bay.copy()
    installed = []
    t_delivered = np.zeros(vehicles)
    # time vehicle finishes delivering bay 

    t_built = {factory: [] for factory in facts}
    avail_cars = []
    car_loc = [(0,0)]*vehicles
    print(car_loc)

    bays = []
    for factory, assigned_bays in fact_bay.items():
        for bay in assigned_bays:
            bays.append(bay)
    print(bays)
    bays = sort_by_dist(bays, (0,0)) # enable comparison in while loop
    print(bays)


    while installed != bays:
        for i in range(vehicles):
            # car has finished delivery + install
            if t == t_delivered[i]:
                avail_cars.append(i)
        
        # building a new bay
        for fact in facts:
            if len(buffer[fact]) < 2 and len(planned[fact]) > 0:
                if len(buffer[fact]) == 1: # buffer is not empty
                    if t >= t_built[fact][0]: # previous bay assembled
                        build_bay = planned[fact].pop(0)
                        t_built[fact].append(build(build_bay, t))
                        buffer[fact].append(build_bay)
                else: # buffer is empy
                    build_bay = planned[fact].pop(0)
                    t_built[fact].append(build(build_bay, t))
                    buffer[fact].append(build_bay)

            if len(avail_cars) > 0 and len(buffer[fact]) > 0:
                if t >= t_built[fact][0]:
                    t_built[fact].pop(0)
                    deliver_bay = buffer[fact].pop(0)
                    installed.append(deliver_bay)

                    car_min_dist = np.inf
                    car_min = 0
                    # sorting available cars by distance to factory in question, call closest car
                    for c in range(len(avail_cars)): # avail_cars: 2, 0, 1
                        car_dist = dist(car_loc[avail_cars[c]], fact)
                        if car_dist < car_min_dist:
                            car_min_dist = car_dist
                            car_min = c
                    car = avail_cars.pop(car_min)
                    t_delivered[car], car_next = deliver(fact, deliver_bay, t, car_loc[car])
                    car_loc[car] = car_next

        installed = sort_by_dist(installed, (0,0))
        
        print("t = %i" %t)
        print("Planned: {}".format(planned))
        print("Built: {}".format(t_built))
        print("Buffer: {}".format(buffer))
        print("Installed: {}".format(installed))
        print("Available Cars: {}".format(avail_cars))
        print("Return Cars: {}".format(t_delivered))

        t += 1

    t_finish = np.max(t_delivered)
    print("Finish Building at t = %i" %t_finish)
    return t_finish

def build(bay, t):
    T_bay = 5 # 4-5 min to assembly
    t_built = t + T_bay
    return t_built

def deliver(fact, bay, t, car_cur):
    v = 400 # 24 km/h = 400 m/min
    T_install = 6 # 6 min to install

    dist_retrieve = dist(car_cur, fact)
    dist_deliver = dist(fact, bay)
    car_next = bay # car's next location is at delivered bay
    t_travel = np.ceil((dist_retrieve + dist_deliver) / v)
    t_delivered = t + t_travel + T_install
    return t_delivered, car_next

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
        sort = True
        run_factory(fact, bays, i, sort)

# testing reducing build time with different factory locations
def test_factories(vehicles, facts, bays, sort):
    t_finish=[]
    for fact in facts:
        #print("Factory: {}".format(fact))
        sort = True
        t_finish.append(run_factory(fact, bays, vehicles, sort))
    return t_finish

# testing reducing build time by sorting bays by distance
def test_sort(vehicles, fact, bays):
    sort = False
    run_factory(fact, bays, vehicles, sort)

    sort = True
    run_factory(fact, bays, vehicles, sort)

if __name__ == "__main__":
    #run_factory_float(facts, fact_bay, vehicles)

    facts = [(0,0),(10,10),(20,20)]
    fact_bay = {(0,0): [(1,2),(1,3),(1,4)], (10,10): [(9,8),(10,8)], (20,20): [(6,6)]}
    vehicles = 3
    run_factory_float(facts, fact_bay, vehicles)