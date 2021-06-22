from pathlib import Path
from threading import Thread
from typing import List

from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID


def _handle_vehicle(sid: SimulationID, vid: str, requests: List[str]) -> None:
    """ Since we are using BeamNG we do not have to control the car, but if we want to read the data we need to call wait_for_simulator_request"""
    from drivebuildclient.aiExchangeMessages_pb2 import VehicleID, SimStateResponse, DataRequest, Control
    from keyboard import is_pressed
    vid_obj = VehicleID()
    vid_obj.vid = vid

    while True:
        print(sid.sid + ": Test status: " + service.get_status(sid))
        print(vid + ": Wait")
        # Read data
        sim_state = service.wait_for_simulator_request(sid, vid_obj)  # wait()
        if sim_state is SimStateResponse.SimState.RUNNING:
            print(vid + ": Request data")
            request = DataRequest()
            request.request_ids.extend(requests)
            data = service.request_data(sid, vid_obj, request)  # request()
            print(data)
        else:
            print(sid.sid + ": The simulation is not running anymore (State: "
                  + SimStateResponse.SimState.Name(sim_state) + ").")
            print(sid.sid + ": Final result: " + service.get_result(sid))
            break


if __name__ == "__main__":
    service = AIExchangeService("localhost", 8383)

    # Send tests - TODO For the moment use test, test for login
    submissions = service.run_tests("test", "test", Path("../examples/BeamNG.AI"))

    # Interact with a simulation
    if submissions:
        submissions = submissions.submissions
    else:
        exit(1)
    for _, sid in submissions.items():
        print ("SID", sid.sid)
        # Those key must match what's inside ../examples/BeamNG.AI/criteriaA.dbc.xml
        ego_requests = ["egoPosition", "egoSpeed" , "egoSteeringAngle"]
        ego_vehicle = Thread(target=_handle_vehicle, args=(sid, "ego", ego_requests))
        ego_vehicle.start()