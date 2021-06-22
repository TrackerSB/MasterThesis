from beamngpy import BeamNGpy

beamng_user_path = "G:\\gitrepos\\BeamNG_user_path"
beamng_install_path = "G:\\gitrepos\\beamng-research_unlimited\\trunk"
parallel = True


def create_instance(i: int) -> BeamNGpy:
    from beamngpy import Scenario, Vehicle
    bng = BeamNGpy("localhost", 64523 + i * 100, home=beamng_install_path, user=beamng_user_path)
    scenario = Scenario("smallgrid", "Instance_" + str(i), authors="Stefan Huber",
                        description="Check execution of multiple BeamNG instances simultaneously.")

    ego_vehicle = Vehicle('ego_vehicle', model='etk800', licence='EGO')
    scenario.add_vehicle(ego_vehicle)

    scenario.make(bng)
    bng.open()
    bng.load_scenario(scenario)
    bng.start_scenario()
    bng.hide_hud()
    ego_vehicle.control(parkingbrake=0, throttle=1.0)
    return bng


def main() -> None:
    from multiprocessing import Process
    instances = []

    try:
        for i in range(1, 3):
            if parallel:
                process = Process(target=create_instance, args=(i,))
                process.start()
            else:
                instances.append(create_instance(i))

        input("Press enter to stop all instances...")
    finally:
        for i in instances:
            i.close()


if __name__ == "__main__":
    main()
