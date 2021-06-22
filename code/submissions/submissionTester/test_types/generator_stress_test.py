from logging import getLogger

from dataclasses import dataclass, field
from datetime import datetime
from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID
from drivebuildclient import static_vars
from pathlib import Path
from typing import Any, List

from util import silence_stdout


@dataclass
class GeneratorStressStat:
    started: datetime = None
    finished: datetime = None
    num_tests: int = 0
    valid_tests: List[SimulationID] = field(default_factory=list)


_logger = getLogger("SubmissionTester.TestTypes.GeneratorStressTest")


def _prepare_tests_for_validity_check(dbe_path: Path, dbc_path: Path) -> None:
    from util import is_dbc
    from xml_util import parse_xml, findall
    from lxml.etree import tostring
    from test_types import set_failure_tag
    dbc_tree = parse_xml(dbc_path)
    if is_dbc(dbc_tree):
        # Remove empty ai tags
        ai_nodes = findall(dbc_tree, "//db:ai")
        for node in ai_nodes:
            if not node.getchildren():
                node.getparent().remove(node)
        set_failure_tag(dbc_tree)
    else:
        _logger.debug("The DBC path \"" + dbc_path.as_posix() + "\" does not contain a DBC.")
    with open(dbc_path.as_posix(), "wb") as file:
        file.write(tostring(dbc_tree))


@static_vars(max_parallel_tests=2)
def generator_stress_test(service: AIExchangeService, generator: Any, max_time: float) -> GeneratorStressStat:
    """
    Checks how many tests the given generator can generate within the given time and whether the generated tests are
    valid.
    :param generator: The generator to check.
    :param max_time: The time the generator has to generate tests (in minutes).
    :return: A dict that maps (isValid --> num of tests).
    """
    from threading import Thread
    from reference.generator import ReferenceTestGenerator
    from datetime import datetime
    from test_types import get_vids_by_path
    from util import join_all
    from drivebuildclient.aiExchangeMessages_pb2 import VehicleID, TestResult
    # Run stress test
    stat = GeneratorStressStat()
    stop_thread = False
    forced_result = TestResult()
    forced_result.result = TestResult.Result.SKIPPED

    def _handle_ai(sid: SimulationID, vid: VehicleID) -> None:
        from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse
        # NOTE Assumes that the car is in _BEAMNG mode
        while not stop_thread:
            sim_state = service.wait_for_simulator_request(sid, vid)
            if sim_state != SimStateResponse.SimState.RUNNING:
                break
        else:
            service.control_sim(sid, forced_result)

    def _stress_generator(generator: Any) -> None:
        stat.started = datetime.now()
        while not stop_thread:
            with silence_stdout():
                all_tests = []
                for i in range(0, generator_stress_test.max_parallel_tests):
                    test = generator.getTest()
                    if test:
                        stat.num_tests = stat.num_tests + 1
                        # Check validity of generated tests
                        _prepare_tests_for_validity_check(*test)
                        reference_dbc = ReferenceTestGenerator.create_reference_test(*test)
                        all_tests.append(test[0])
                        all_tests.append(reference_dbc)
                submission_result = service.run_tests("test", "test", test[0], reference_dbc)
                if submission_result and submission_result.submissions:
                    ai_threads = []
                    for _, sid in submission_result.submissions.items():
                        stat.valid_tests.append(sid)
                        _, vids = get_vids_by_path(reference_dbc)
                        for vid in vids:
                            thread = Thread(target=_handle_ai, args=(sid, vid))
                            thread.start()
                            ai_threads.append(thread)
                    join_all(ai_threads, max_time * 60)
        stat.finished = datetime.now()

    stress_process = Thread(target=_stress_generator, args=(generator,))
    stress_process.daemon = True
    stress_process.start()
    stress_process.join(max_time * 60)
    stop_thread = True
    stress_process.join()
    return stat
