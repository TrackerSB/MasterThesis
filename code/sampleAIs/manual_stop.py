from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, TestResult

if __name__ == "__main__":
    sid = SimulationID()
    sid.sid = "snid_3_sim_5714"
    result = TestResult()
    result.result = TestResult.Result.FAILED
    service = AIExchangeService("defender.fim.uni-passau.de", 8383)
    service.control_sim(sid, result)
