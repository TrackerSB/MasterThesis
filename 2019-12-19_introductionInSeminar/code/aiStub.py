class MyFancyAI:
    from drivebuildclient.AIExchangeService import AIExchangeService
    from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID, SimStateResponse, DataRequest, Control

    def __init__(self, AIExchangeService) -> None:
        self._service = service

    def start(self, sid: SimulationID, vid: VehicleID) -> None:
        while True:
            print(sid.sid + ": Test status: " + service.get_status(sid))
            sim_state = service.wait_for_simulator_request(sid, vid)
            if sim_state is SimStateResponse.SimState.RUNNING:
                request = DataRequest()
                request.request_ids.extend(["<requestIDs>"])
                data = service.request_data(sid, vid, request)
                control = Control()  # TODO Specify control commands
                service.control(sid, vid, control)
            else:
                print(sid.sid + ": The simulation finished (Final state: "
                      + SimStateResponse.SimState.Name(sim_state) + ").")
                print(sid.sid + ": Final test result: " + service.get_result(sid))
                # Clean up everything you have to
                break
