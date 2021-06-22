from beamngpy import BeamNGpy, Scenario, Vehicle

# Instantiate BeamNGpy instance running the simulator from the given path,
# communicating over localhost:64256
bng = BeamNGpy('localhost', 64256, home="G:\\gitrepos\\beamng-research_unlimited\\trunk")
# Create a scenario in west_coast_usa called 'example'

scenario = Scenario('west_coast_usa', 'example')

vehicle1 = Vehicle('ego_vehicle', model='etk800', licence='EGO-CAR', color='Red')
vehicle2 = Vehicle('ego_vehicle2', model='etk800', licence='CAR', color='Blue')

# Add it to our scenario at this position and rotation
scenario.add_vehicle(vehicle1, pos=(-717, 101, 118), rot=(0, 0, 45))
scenario.add_vehicle(vehicle2, pos=(-717, 110, 118), rot=(0, 0, 45))

# scenario.add_vehicle(vehicle, pos=(19, 122, 0), rot=(0, 0, 45))  # this position for GridMap
# Place files defining our scenario for the simulator to read
scenario.make(bng)

# Launch BeamNG.research
bng.open()
try:
    # Load and start our scenario
    bng.load_scenario(scenario)
    bng.start_scenario()

    # vehicle.ai_set_speed(50,mode='set')
    # Make the vehicle's AI span the map
    # vehicle1.ai_set_mode('span')
    # vehicle2.ai_set_mode('span')
    while True:
        pass
finally:
    bng.close()
