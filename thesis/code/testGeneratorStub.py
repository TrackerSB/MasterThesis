from drivebuildclient.aiExchangeMessage_pb2 import SimulationID, VehicleID, DataResponse
from pathlib import Path
from typing import Optional, Tuple

class TestGenerator:
    def getTest() -> Optional[Tuple[Path, Path]]:
        # NOTE The first path points to the DBE, the second to the DBC
        raise NotImplementedError("Not implemented, yet.")

