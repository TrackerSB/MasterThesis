import os
from typing import Union, Callable

from beamngpy import BeamNGpy, Scenario


def get_home_dir() -> str:
    return 'G:/gitrepos/beamng-research_unlimited/trunk'


def get_user_dir() -> str:
    dir_path: Union[bytes, str] = os.path.dirname(os.path.realpath(__file__))
    return dir_path + '/../BeamNGUserPath/'


def create_scenario(create: Callable[[BeamNGpy, Scenario], None], handle: Callable[[BeamNGpy, Scenario], None]) -> None:
    # Setup BeamNG
    bng: BeamNGpy = BeamNGpy('localhost', 64256, home=get_home_dir(), user=get_user_dir())
    bng_scenario: Scenario = Scenario('smallgrid', 'experiment', authors='Stefan Huber')

    # Call the definition of the scenario
    create(bng, bng_scenario)
    bng_scenario.make(bng)

    # Start simulation
    bng.open(launch=True)
    try:
        bng.load_scenario(bng_scenario)
        bng.start_scenario()

        # Handle the running simulation
        handle(bng, bng_scenario)

        input("Press enter to end simulation...")
    finally:
        bng.close()
