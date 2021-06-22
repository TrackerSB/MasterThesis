from typing import Callable

from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import VehicleID, SimulationID
from lxml.etree import _Element


class ReferenceAI:
    def __init__(self, service: AIExchangeService):
        self.service = service

    def start(self, sid: SimulationID, vid: VehicleID, dynamic_stats_callback: Callable[[], None]) -> None:
        from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse
        # NOTE Assumes that the car is in _BEAMNG mode
        while True:
            sim_state = self.service.wait_for_simulator_request(sid, vid)
            dynamic_stats_callback()
            # FIXME Control command required?
            if sim_state != SimStateResponse.SimState.RUNNING:
                break

    @staticmethod
    def add_data_requests(ai_tag: _Element, participant_id: str) -> None:
        pass
