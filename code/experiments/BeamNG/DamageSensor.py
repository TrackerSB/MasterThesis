from time import sleep

from beamngpy import Scenario, Vehicle, BeamNGpy
from beamngpy.sensors import Damage

from template import create_scenario


def setup(bng: BeamNGpy, bng_scenario: Scenario) -> None:
    ego_vehicle: Vehicle = Vehicle('ego_vehicle', model='etk800', licence='EGO', color='white')
    damage_sensor: Damage = Damage()
    ego_vehicle.attach_sensor('damage', damage_sensor)
    bng_scenario.add_vehicle(ego_vehicle, pos=(0, 0, 10), rot=(90, 0, 0))


def handle(bng: BeamNGpy, bng_scenario: Scenario) -> None:
    ego_vehicle: Vehicle = bng_scenario.get_vehicle('ego_vehicle')
    while True:
        sleep(1)
        ego_vehicle.update_vehicle()
        sensors = bng.poll_sensors(ego_vehicle)
        damage_data = sensors['damage']
        print(damage_data)

        bng.step(3, wait=False)


if __name__ == '__main__':
    create_scenario(setup, handle)
