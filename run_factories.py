import numpy as np
import scipy as sp
import scipy.spatial.distance as spd
import copy

def run_factories(factory_assignments, vehicles):
    # facts: list of factory locations, used to index fact_bay
    # fact_bay: dictionary of bays assigned to factories
    t = 0

    # site trackers
    n_factories = len(list(factory_assignments.keys()))
    loc_list = list(factory_assignments[0].keys()) # all factory locations
    n_locations = len(loc_list)
    planned = copy.deepcopy(factory_assignments)
    installed = []
    bays = []
    for j in range(n_factories):
        for fact, assigned_bays in planned[j].items():
            for bay in assigned_bays:
                bays.append(bay)

    # factory trackers
    buffer = {j: [] for j in range(n_factories)}
    t_built = {j: [] for j in range(n_factories)}
    t_moved = np.zeros(n_factories) # keep track of move-finish times for each factory
    fact_index = np.zeros(n_factories, dtype=int) # factory's current location index
    cur_fact = [(0,0)]*n_factories # factory's current location
    fact_complete = np.zeros(n_factories) # = 1 when no more factory locations for factory j
    factory_start_time = {j: [] for j in range(n_factories)} # = -1 if no bays assigned 
    factory_finish_time = {j: [] for j in range(n_factories)}

    #vehicle trackers
    t_delivered = np.zeros(vehicles) # time each vehicle finishes delivery
    avail_cars = []
    car_loc = [(0,0)]*vehicles

    # initializing first location for each factory
    for j in range(n_factories):
        for l in range(n_locations):
            fact = loc_list[l]
            #print(f"Planned structure: {planned}")
            #print(f"Accessing planned[{j}][{fact}]")
            if len(planned[j][fact]) > 0:
                fact_index[j] = l
                cur_fact[j] = fact
                factory_start_time[j].append(0)
                break
            else:
                factory_start_time[j].append(-1)
                factory_finish_time[j].append(-1)

    while len(installed) < len(bays):
        for i in range(vehicles):
            # car has finished delivery + install
            if t == t_delivered[i]:
                avail_cars.append(i)

        # resorting facts so that no single fact hogs the newly available car
        remaining = [len(planned[j][cur_fact[j]]) for j in range(n_factories)]
        j_sorted = [j for _, j in sorted(zip(remaining, [j for j in range(n_factories)]), reverse=True)]

        for j in j_sorted:
            if len(buffer[j]) < 2 and len(planned[j][cur_fact[j]]) > 0 and t >= t_moved[j]:
                # factory has finished moving, can build a bay
                if (len(buffer[j]) == 1 and t >= t_built[j][0]) or len(buffer[j]) == 0:
                    # previous bay assembled or buffer is empty
                    build_bay = planned[j][cur_fact[j]].pop(0)
                    t_built[j].append(build(t))
                    buffer[j].append(build_bay)

            elif len(planned[j][cur_fact[j]]) == 0 and fact_complete[j] == 0 and len(buffer[j]) == 0:
                # for this factory, all bays at this location have been installed
                prev_fact = cur_fact[j]
                factory_finish_time[j].append(t)
                # only check factories after current factory
                for l in range(fact_index[j]+1, n_locations):
                    if len(planned[j][loc_list[l]]) > 0: # if next location has assigned bays
                        fact_index[j] = l
                        cur_fact[j] = loc_list[l] # set new factory location for factory j
                        break
                    else:
                        factory_start_time[j].append(-1)
                        factory_finish_time[j].append(-1)
                if prev_fact == cur_fact[j]:
                    # signifies that there are no more factory locations for factory j
                    fact_complete[j] = 1
                else:
                    factory_start_time[j].append(t) # i think it makes more sense to signify a location's
                    # start as when the factory is relocated there
                    t_moved[j] = move(t)
                    #factory_start_time.append(t_moved[j])
            
            if len(avail_cars) > 0 and len(buffer[j]) > 0:
                if t >= t_built[j][0]:
                    # if there are available cars and bays that can be relieved
                    t_built[j].pop(0)
                    deliver_bay = buffer[j].pop(0)
                    installed.append(deliver_bay)

                    car_min_dist = np.inf
                    car_min = 0
                    # sorting available cars by distance to factory in question
                    for c in range(len(avail_cars)): # avail_cars: 2, 0, 1
                        car_dist = dist(car_loc[avail_cars[c]], fact)
                        if car_dist < car_min_dist:
                            car_min_dist = car_dist
                            car_min = c
                    car = avail_cars.pop(car_min)
                    fact = cur_fact[j]
                    t_delivered[car], car_next = deliver(fact, deliver_bay, t, car_loc[car])
                    car_loc[car] = car_next
        # if t % 5000 == 0:
        #print("t = %i" %t)
        #for j in range(n_factories):
            #if fact_complete[j] == 1:
                #print("Factory {} is completed".format(j))
            #elif t < t_moved[j]:
                #print("Factory {} is moving to {}".format(j, cur_fact[j]))
            #else:
                #print("Factory {} is at location {}, {}".format(j, fact_index[j], cur_fact[j]))
                #print("Buffer length: {}".format(len(buffer[j])))
                #print("Remaining bays at this location: {}".format(len(planned[j][cur_fact[j]])))

        t += 1

    t_finish = np.max(t_delivered)
    cost = estimate_cost(t_finish, vehicles, n_factories)
    print("Finish Building at t = %i min" %t_finish)
    print("Cost estimate: %i USD" %cost)
    return t_finish, factory_start_time, factory_finish_time, cost

def run_factories_ani(factory_assignments, vehicles):
    import numpy as np
    import copy

    # facts: list of factory locations, used to index fact_bay
    # fact_bay: dictionary of bays assigned to factories
    t = 0

    # site trackers
    n_factories = len(list(factory_assignments.keys()))
    loc_list = list(factory_assignments[0].keys())  # all factory locations
    n_locations = len(loc_list)
    planned = copy.deepcopy(factory_assignments)
    installed = []
    bays = []
    for j in range(n_factories):
        for fact, assigned_bays in planned[j].items():
            for bay in assigned_bays:
                bays.append(bay)

    # factory trackers
    buffer = {j: [] for j in range(n_factories)}
    t_built = {j: [] for j in range(n_factories)}
    t_moved = np.zeros(n_factories)  # keep track of move-finish times for each factory
    fact_index = np.zeros(n_factories, dtype=int)  # factory's current location index
    cur_fact = [(0, 0)] * n_factories  # factory's current location
    fact_complete = np.zeros(n_factories)  # = 1 when no more factory locations for factory j
    factory_start_time = {j: [] for j in range(n_factories)}  # = -1 if no bays assigned 
    factory_finish_time = {j: [] for j in range(n_factories)}

    # vehicle trackers
    t_delivered = np.zeros(vehicles)  # time each vehicle finishes delivery
    avail_cars = []
    car_loc = [(0, 0)] * vehicles

    # Bay installation timeline for animation
    bay_timeline = []  # Records (time, bay location)

    # initializing first location for each factory
    for j in range(n_factories):
        for l in range(n_locations):
            fact = loc_list[l]
            if len(planned[j][fact]) > 0:
                fact_index[j] = l
                cur_fact[j] = fact
                factory_start_time[j].append(0)
                break
            else:
                factory_start_time[j].append(-1)
                factory_finish_time[j].append(-1)

    while len(installed) < len(bays):
        for i in range(vehicles):
            # car has finished delivery + install
            if t == t_delivered[i]:
                avail_cars.append(i)

        # resorting facts so that no single fact hogs the newly available car
        remaining = [len(planned[j][cur_fact[j]]) for j in range(n_factories)]
        j_sorted = [j for _, j in sorted(zip(remaining, range(n_factories)), reverse=True)]

        for j in j_sorted:
            if len(buffer[j]) < 2 and len(planned[j][cur_fact[j]]) > 0 and t >= t_moved[j]:
                # factory has finished moving, can build a bay
                if (len(buffer[j]) == 1 and t >= t_built[j][0]) or len(buffer[j]) == 0:
                    # previous bay assembled or buffer is empty
                    build_bay = planned[j][cur_fact[j]].pop(0)
                    t_built[j].append(build(t))
                    buffer[j].append(build_bay)

            elif len(planned[j][cur_fact[j]]) == 0 and fact_complete[j] == 0 and len(buffer[j]) == 0:
                # for this factory, all bays at this location have been installed
                prev_fact = cur_fact[j]
                factory_finish_time[j].append(t)
                # only check factories after current factory
                for l in range(fact_index[j] + 1, n_locations):
                    if len(planned[j][loc_list[l]]) > 0:  # if next location has assigned bays
                        fact_index[j] = l
                        cur_fact[j] = loc_list[l]  # set new factory location for factory j
                        break
                    else:
                        factory_start_time[j].append(-1)
                        factory_finish_time[j].append(-1)
                if prev_fact == cur_fact[j]:
                    # signifies that there are no more factory locations for factory j
                    fact_complete[j] = 1
                else:
                    factory_start_time[j].append(t)  # signify a location's start as when the factory is relocated there
                    t_moved[j] = move(t)

            if len(avail_cars) > 0 and len(buffer[j]) > 0:
                if t >= t_built[j][0]:
                    # if there are available cars and bays that can be relieved
                    t_built[j].pop(0)
                    deliver_bay = buffer[j].pop(0)
                    installed.append(deliver_bay)

                    # Track the time and location of bay installation
                    bay_timeline.append((t, deliver_bay))

                    car_min_dist = np.inf
                    car_min = 0
                    # sorting available cars by distance to factory in question
                    for c in range(len(avail_cars)):
                        car_dist = dist(car_loc[avail_cars[c]], cur_fact[j])
                        if car_dist < car_min_dist:
                            car_min_dist = car_dist
                            car_min = c
                    car = avail_cars.pop(car_min)
                    t_delivered[car], car_next = deliver(cur_fact[j], deliver_bay, t, car_loc[car])
                    car_loc[car] = car_next

        t += 1

    t_finish = np.max(t_delivered)
    return t_finish, factory_start_time, factory_finish_time, bay_timeline


def build(t):
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

def move(t):
    T_move = 60 * 24
    #T_move = 10
    t_moved = t + T_move
    return t_moved

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

def estimate_cost(time, vehicles, factories):
    hours = time / 60

    # factory and vehicle depreciation rate
    d_factory = 10
    d_vehicle = 2

    # labor parameters
    c_labor = 25
    N_factory = 3
    N_field = 3
    N_vehicle = 1
    
    factory_cost = hours * factories * d_factory
    vehicle_cost = hours * vehicles * d_vehicle
    factory_labor = factories * (N_factory + N_field)
    vehicle_labor = vehicles * N_vehicle
    labor_cost = hours * c_labor * (factory_labor + vehicle_labor)

    total_cost = factory_cost + vehicle_cost + labor_cost
    return total_cost

if __name__ == "__main__":
    factory_assignments = {0: {(0,0): [(100,100),(200,200)],
                                (10,10): [],
                                (20,20): [(300,300)],
                                (30,30): []},
                            1: {(0,0): [],
                                (10,10): [(150,150)],
                                (20,20): [],
                                (30,30): [(250,250)]}}
    run_factories(factory_assignments, 3)