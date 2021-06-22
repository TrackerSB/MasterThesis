from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID

service = AIExchangeService("defender.fim.uni-passau.de", 8383)
ego = VehicleID()
ego.vid = "ego"
non_ego = VehicleID()
non_ego.vid = "nonEgo"


def start(sid: SimulationID, vid: VehicleID) -> None:
    from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse, DataRequest
    request = DataRequest()
    request.request_ids.extend([vid.vid + "Position"])
    while True:
        sim_state = service.wait_for_simulator_request(sid, vid)
        data = service.request_data(sid, vid, request)
        print(data)
        if sim_state != SimStateResponse.SimState.RUNNING:
            break


def main() -> None:
    from pathlib import Path
    from threading import Thread
    submission_result = service.run_tests("test", "test", Path("criteria0.dbc.xml"), Path("environment.dbe.xml"))
    if submission_result and submission_result.submissions:
        for _, sid in submission_result.submissions.items():
            ego_thread = Thread(target=start, args=(sid, ego))
            ego_thread.start()
            non_ego_thread = Thread(target=start, args=(sid, non_ego))
            non_ego_thread.start()
            ego_thread.join()
            non_ego_thread.join()
            print(service.get_result(sid))
    else:
        print("Submitted tests were invalid.")
        print(submission_result.message.message)


if __name__ == "__main__":
    main()
