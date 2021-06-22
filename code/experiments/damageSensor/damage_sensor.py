beamng_user_path = "G:\\gitrepos\\BeamNG_user_path"
beamng_install_path = "G:\\gitrepos\\beamng-research_unlimited\\trunk"


def main() -> None:
    from beamngpy import BeamNGpy, Scenario, Vehicle, ProceduralCube
    from beamngpy.sensors import Damage
    from time import sleep
    bng = BeamNGpy("localhost", 64523, home=beamng_install_path, user=beamng_user_path)
    scenario = Scenario("smallgrid", "DamageSensorTest", authors="Stefan Huber",
                        description="Test usage and check output of the damage sensor")

    ego_vehicle = Vehicle('ego_vehicle', model='etk800', licence='EGO', color='Red')
    ego_vehicle.attach_sensor("damage", Damage())
    scenario.add_vehicle(ego_vehicle, rot=(0, 0, -90))

    another_vehicle = Vehicle('another_vehicle', model='etk800', licence='EGO', color='Blue')
    scenario.add_vehicle(another_vehicle, pos=(10, 0, 0))

    wall = ProceduralCube((100, 0, 3), (0, 0, 0), (10, 1, 6))
    scenario.add_procedural_mesh(wall)

    scenario.make(bng)
    bng.open()
    try:
        bng.load_scenario(scenario)
        bng.start_scenario()
        bng.hide_hud()
        ego_vehicle.control(parkingbrake=0, throttle=1.0)
        while True:
            sensor_data = bng.poll_sensors(ego_vehicle)
            print(sensor_data["damage"])
            sleep(1)
    finally:
        bng.close()


if __name__ == "__main__":
    main()
