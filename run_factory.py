import numpy as np

def run_factory(fact, bays, vehicles):
    t = 0
    buffer = []
    installed = []
    t_return = np.zeros(vehicles)
    t_built = []
    avail_cars = []
    planned = list(bays)

    while installed != bays:
        for i in range(vehicles):
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
        print("t = %i" %t)
        print("Planned: {}".format(planned))
        print("Built: {}".format(t_built))
        print("Buffer: {}".format(buffer))
        print("Installed: {}".format(installed))
        print("Available Cars: {}".format(avail_cars))
        print("Return Cars: {}".format(t_return))

        t += 1
    print("Finish Building at t = %i" %np.max(t_return))

def build(bay, t):
    T_bay = 5
    t_built = t + T_bay
    return t_built

def deliver(fact, bay, t):
    v = 0.4
    T_install = 6

    distance = dist(fact, bay)
    travel = 2 * np.ceil(distance / v)
    t_return = t + travel + T_install
    return t_return

def dist(fact, bay):
    x_dist = np.abs(fact[0] - bay[0])
    y_dist = np.abs(fact[1] - bay[1])
    return x_dist + y_dist

vehicles = 2
bays = [(1,1), (1,2), (1,3)]
fact = (0,0)
run_factory(fact, bays, vehicles)