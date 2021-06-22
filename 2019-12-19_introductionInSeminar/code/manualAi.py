if __name__ == "__main__":
    from pathlib import Path
    from drivebuildclient.AIExchangeService import AIExchangeService
    from drivebuildclient.aiExchangeMessages_pb2 import VehicleID
    service = AIExchangeService("localhost", 8383)

    # Send tests
    submission_result = service.run_tests("test", "test", Path("criteriaA.dbc.xml"), Path("environmentA.dbe.xml"))

    # Interact with a simulation
    if submission_result and submission_result.submissions:
        for test_name, sid in submission_result.submissions.items():
            vid = VehicleID()
            vid.vid = "<vehicleID>"
            MyFancyAI(service).start(sid, vid)

