def main() -> None:
    from beamngpy import BeamNGpy, Scenario, Vehicle
    from time import sleep
    bng = BeamNGpy("localhost", 64523, home="G:\\gitrepos\\beamng-research_unlimited\\trunk",
                   user="G:\\gitrepos\\BeamNG_user_path")
    scenario = Scenario("smallgrid", "OrientationTest", authors="Stefan Huber",
                        description="Check how the orientation in BeamNG works.")
    vehicle_0 = Vehicle("vehicleA", model="etk800", color="White", licence="0")
    scenario.add_vehicle(vehicle_0, pos=(0, 0, 0), rot=(0, 0, 0))
    vehicle_90 = Vehicle("vehicleB", model="etk800", color="Red", licence="90")
    scenario.add_vehicle(vehicle_90, pos=(10, 0, 0), rot=(0, 0, 90))
    scenario.make(bng)
    bng.open()
    try:
        bng.load_scenario(scenario)
        bng.start_scenario()
        while True:
            sleep(1)
    finally:
        bng.close()


if __name__ == "__main__":
    main()
