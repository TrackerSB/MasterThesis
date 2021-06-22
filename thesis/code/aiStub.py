from drivebuildclient.aiExchangeMessage_pb2 import SimulationID, VehicleID, SimStateResponse
from drivebuildclient.AIExchangeService import AIExchangeService
from lxml.etree import _Element

class AI:
    def __init__(self, service: AIExchangeService):
        self.service = service

    @staticmethod
    def add_data_requests(ai_tag: _Element, participant_id: str) -> None:
        raise NotImplementedError("Not implemented, yet.")

    def start(self, sid: SimulationID, vid: VehicleID, add_dynamic_stats: Callable[[], None]) -> None:
        while True:
            sim_state = self.service.wait_for_simulator_request(sid, vid)
            if sim_state == SimStateResponse.SimState.RUNNING:
                add_dynamic_stats()  # Allows the evaluation to introduce further calls to DriveBuild
                # Request data
                # Control AV or simulation
            else:
                break

