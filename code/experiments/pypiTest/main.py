def main() -> None:
    from client.AIExchangeService import AIExchangeService
    from common.aiExchangeMessages_pb2 import TestResult, SimulationID
    from pathlib import Path
    service = AIExchangeService("localhost", 8383)
    sids = service.run_tests("test", "test", Path("../../examples/StefanHuber"))
    if sids:
        for sid in sids.sids:
            sid_obj = SimulationID()
            sid_obj.sid = sid
            result = TestResult()
            result.result = TestResult.Result.FAILED
            service.control_sim(sid_obj, result)


if __name__ == "__main__":
    main()
