import msgpack
from beamngpy import BNGError, BNGValueError


def main() -> None:
    from beamngpy import BeamNGpy
    from beamngpy import Scenario
    from beamngpy import Vehicle
    from beamngpy.sensors import GForces
    beamng = BeamNGpy("localhost", 64256, "G:\\gitrepos\\beamng-research_unlimited\\trunk", "G:\\gitrepos\\BeamNGUserHome")
    scenario = Scenario('west_coast_usa', 'lidar_tour',
                        description='Tour through the west coast gathering '
                                    'Lidar data')

    vehicle = Vehicle('ego_vehicle', model='etk800', licence='LIDAR')
    # gforces = GForces()
    # vehicle.attach_sensor("gforcesID", gforces)
    scenario.add_vehicle(vehicle, pos=(-717.121, 101, 118.675), rot=(0, 0, 45))
    scenario.make(beamng)

    bng = beamng.open(launch=True)
    try:
        bng.load_scenario(scenario)

        bng.set_steps_per_second(60)
        bng.set_deterministic()

        bng.hide_hud()
        bng.start_scenario()

        vehicle.ai_set_mode('span')

        while True:
            # Encode request
            req = dict(type='GForces')
            reqs = dict()
            reqs['gforcesReq'] = req
            reqs = dict(type='SensorRequest', sensors=reqs)

            # Request data
            sensorData = dict()
            # Send request
            data = msgpack.packb(reqs, use_bin_type=True)
            length = '{:016}'.format(len(data))
            skt = vehicle.skt # FIXME Do NOT access socket by this
            skt.send(bytes(length, 'ascii'))
            skt.send(data)
            # Receive request
            length = skt.recv(16)
            length = int(str(length, 'ascii'))
            buf = bytearray()
            while length > 0:
                chunk = min(4096, length)
                received = skt.recv(chunk)
                buf.extend(received)
                length -= len(received)
            assert length == 0
            data = msgpack.unpackb(buf, raw=False)
            if 'bngError' in data:
                raise BNGError(data['bngError'])
            if 'bngValueError' in data:
                raise BNGValueError(data['bngValueError'])
            response = data
            assert response['type'] == 'SensorData'
            sensorData.update(response['data'])

            # Print data
            print(sensorData)

    finally:
        bng.close()


if __name__ == "__main__":
    main()
