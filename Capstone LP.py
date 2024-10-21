import pulp as pl

# === Parameters ===

# Installation Times
production_time_per_bay = 4.5 / 60  # 4.5 minutes in hours
added_time_per_module = 38 / 3600  # 38 seconds in hours
installation_time_per_bay = 6 / 60  # 6 minutes in hours
truck_speed_kmph = 24  # km/h

# Depreciation
lifetime_of_factory = 100000  # hours
cost_per_factory = 1000000  # USD
lifetime_of_vehicle = 75000  # hours
cost_per_vehicle = 150000  # USD
factory_depreciation_rate = 10  # USD/hour
vehicle_depreciation_rate = 2  # USD/hour

# Inputs
deadline = 3  # Maximum time of 5 hours to complete the project

x_factories = 3  # Factories available
x_vehicles = 12  # Vehicles available
n_bays_in_site = 50  # Total number of bays

# Vehicle speed
V_truck = 24  # Speed of the truck in km/h

# === Decision Variables ===
problem = pl.LpProblem("Minimize_Total_Cost", pl.LpMinimize)

# Distance between factories (continuous variable)
D_f = pl.LpVariable.dicts("Factory_Distance", range(x_factories), lowBound=0, cat="Continuous")

# Travel time between factories (continuous variable)
T_travel = pl.LpVariable.dicts("Travel_Time", range(n_bays_in_site), lowBound=0, cat="Continuous")

# Number of factories required (integer)
y_factories = pl.LpVariable("Factories_Required", lowBound=1, cat="Integer")  # Ensure minimum 1 factory

# Number of vehicles required (integer)
y_vehicles = pl.LpVariable("Vehicles_Required", lowBound=1, cat="Integer")  # Ensure minimum 1 vehicle

# === Objective Function ===
# Minimize total project costs, including vehicle and factory costs
problem += (
    # Factory depreciation cost (based on the deadline of 5 hours)
    factory_depreciation_rate * y_factories * deadline +
    
    # Vehicle depreciation cost (based on the deadline of 5 hours)
    vehicle_depreciation_rate * y_vehicles * deadline +
    
    # Cost of moving factories (proportional to distance)
    pl.lpSum(D_f[i] * factory_depreciation_rate for i in range(x_factories)) +
    
    # Total cost of factories and vehicles
    cost_per_factory * y_factories + cost_per_vehicle * y_vehicles
), "Minimize_Total_Cost"

# === Constraints ===

# Number of factories cannot exceed the available factories
problem += y_factories <= x_factories, "Max_Factories"

# Number of vehicles cannot exceed the available vehicles
problem += y_vehicles <= x_vehicles, "Max_Vehicles"

# Constraint to link travel time to distance and vehicle speed (fixed with multiplication)
for r in range(n_bays_in_site):
    problem += T_travel[r] == D_f[r % x_factories] * (1 / V_truck), f"Travel_Time_Constraint_{r}"

# Total time per bay (production + installation + travel)
total_time_per_bay = production_time_per_bay + installation_time_per_bay + sum(T_travel[r] for r in range(n_bays_in_site)) / n_bays_in_site

# Maximum number of bays a single vehicle can handle within the deadline
# total_time_per_bay * bays_per_vehicle <= deadline
# We derive the constraint to ensure that y_vehicles is sufficient to handle all bays within the deadline
problem += y_vehicles >= (n_bays_in_site * total_time_per_bay) / deadline, "Vehicle_Time_Constraint"

# === Solve the problem ===
problem.solve()

# Calculate the total cost based on the solution
total_cost = (
    factory_depreciation_rate * y_factories.varValue * deadline +
    vehicle_depreciation_rate * y_vehicles.varValue * deadline +
    sum(D_f[i].varValue * factory_depreciation_rate for i in range(x_factories)) +
    cost_per_factory * y_factories.varValue + cost_per_vehicle * y_vehicles.varValue
)

# === Calculate Total Project Time After Solving ===
# Calculate the total time per bay (including travel, production, and installation time)
final_total_time_per_bay = (
    production_time_per_bay + installation_time_per_bay + sum(T_travel[r].varValue for r in range(n_bays_in_site)) / n_bays_in_site
)

# Calculate the total project time based on the number of vehicles used
final_total_project_time = (n_bays_in_site / y_vehicles.varValue) * final_total_time_per_bay

# === Output the results ===
print(f"Status: {pl.LpStatus[problem.status]}")

# Display Results
print(f"Number of Bays: {n_bays_in_site}")
print(f"Factories Required: {y_factories.varValue}")
print(f"Vehicles Required: {y_vehicles.varValue}")
print(f"Total Cost: {total_cost:.2f} USD")
print(f"Total Project Time: {final_total_project_time:.2f} hours (Max Deadline: {deadline} hours)")
