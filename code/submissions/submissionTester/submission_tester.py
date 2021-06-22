from enum import Enum
from logging import getLogger, basicConfig, INFO, WARNING

from datetime import datetime
from drivebuildclient import static_vars
from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.db_handler import DBConnection
from pathlib import Path
from typing import List, Any, Dict, Tuple, Union, Callable, Optional

from reference.ai import ReferenceAI
from util import silence_stdout

with silence_stdout():
    import SwaminathanGopalHarish.swamin01_xml.map as SGHarish
    import TymofyeyevVsevolod.ai as TymofyeyevV
    import VoglSebastian.TestGenerator.TestGenerator as VoglSebastian
    import LandauMarco.main as LandauMarco
    from reference.generator import RandomGenerator
    from AsenSebastian import Test as AsenSebastian
    from GambiAlessio import main as GambiAlessio
    import self_driving.drivebuild as DeepJanus2020


class TestType(Enum):
    TEST_GENERATOR = 0
    AI_TEST = 1
    RUN_FILE = 2


_logger = getLogger("SubmissionTester.SubmissionTester")
service = AIExchangeService("defender.fim.uni-passau.de", 8383)
# name --> (submission, TestType, consideredInTests)
submission_map: Dict[str, Tuple[Union[List[Path], Any], TestType, bool]] = {
    "Reference Generator": (RandomGenerator(), TestType.TEST_GENERATOR, True),
    "Sebastian Vogl": (VoglSebastian.TestGenerator(), TestType.TEST_GENERATOR, False),
    "Harish Swaminathan Gopal": (SGHarish.write(), TestType.TEST_GENERATOR, False),
    "Sebastian Asen": (AsenSebastian, TestType.TEST_GENERATOR, False),

    "Reference AI": (ReferenceAI(service), TestType.AI_TEST, False),
    "Vsevolod Tymofyeyev": (TymofyeyevV.DDPGAI(service), TestType.AI_TEST, False),
    "Marco Landau": (LandauMarco.AI(service), TestType.AI_TEST, False),
    "Alessio Gambi": (GambiAlessio.AI(service), TestType.AI_TEST, False),
    "DeepJanus2020": (DeepJanus2020.AI(service), TestType.AI_TEST, True),

    "Steve Banin Panyin": ([Path("../submissions/BaninSteve/final.py")], TestType.RUN_FILE, True),
    "Nguyen Thi Thu Ngan": ([Path("../submissions/ThiThuNganNguyen/NSGAII.py")], TestType.RUN_FILE, True)
}

_DB_CONNECTION = DBConnection("dbms.infosun.fim.uni-passau.de", 5432, "huberst", "huberst", "GAUwV5w72YvviLmb")


class TestMode(Enum):
    GENERATOR_STRESS = 0
    CHALLENGE = 1
    SIMPLE_RUN = 2
    AI_SCALABILITY = 3
    SCALABILITY = 4


def _do_test_stub(implemented_types: Dict[TestType, Callable[[str, Any], None]]) -> Callable[[List[str]], None]:
    def _process(submissions: List[str]) -> None:
        for name in submissions:
            subject, type, considered = submission_map[name]
            if considered:
                if type in implemented_types:
                    implemented_types[type](name, subject)
                else:
                    _logger.warning("Test mode not implemented for " + type.name + ".")
            else:
                _logger.info("Submission " + name + " is not considered.")

    return _process


def _time_to_string(time: datetime) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _do_generator_stress(submissions: List[str], stress_time: float) -> None:
    from test_types.generator_stress_test import generator_stress_test

    def _process_test_generator(name: str, subject: Any) -> None:
        _logger.info("Stress test for " + name + " (Time: " + str(stress_time) + " minutes)")
        stress_stat = generator_stress_test(service, subject, stress_time)
        args = {
            "started": _time_to_string(stress_stat.started),
            "finished": _time_to_string(stress_stat.finished),
            "numTests": stress_stat.num_tests,
            "validTests": [int(sid.sid) for sid in stress_stat.valid_tests] if stress_stat.valid_tests else None,
            "author": name
        }
        _DB_CONNECTION.run_query("""
        INSERT INTO  generatorstresstest(started, finished, numtests, validtests, author) VALUES 
        (:started, :finished, :numTests, :validTests, :author)
        """, args)

    _do_test_stub({TestType.TEST_GENERATOR: _process_test_generator})(submissions)


def _do_challenge_test(submissions: List[str], challenge_time: int, lane_markings: Optional[bool]) -> None:
    from test_types.challenge_test import test_ai_against_generator
    from collections import defaultdict
    opponents = defaultdict(list)
    for name in submissions:
        subject, type, considered = submission_map[name]
        if considered:
            if type in [TestType.TEST_GENERATOR, TestType.AI_TEST]:
                opponents[type].append((name, subject))
            else:
                _logger.warning("Test mode not implemented for " + type.name + ".")
        else:
            _logger.info("Submission " + name + " is not considered.")
    for ai_name, ai in opponents[TestType.AI_TEST]:
        for generator_name, generator in opponents[TestType.TEST_GENERATOR]:
            _logger.info("AI of " + ai_name + " runs against generated tests of " + generator_name)
            challenge_result = test_ai_against_generator(service, generator, ai, challenge_time, lane_markings)

            for gen_stat, ai_stats in challenge_result:
                gen_stat_args = {
                    "sid": gen_stat.sid.sid if gen_stat.sid else None,
                    "started": _time_to_string(gen_stat.started),
                    "finished": _time_to_string(gen_stat.finished),
                    "rejected": gen_stat.rejected,
                    "failed": gen_stat.failed,
                    "author": generator_name,
                    "numLanes": gen_stat.num_lanes,
                    "numSegments": gen_stat.num_segments if gen_stat.num_segments else None,
                    "markings": gen_stat.markings if gen_stat.markings else None,
                    "invalid": gen_stat.invalid
                }
                _DB_CONNECTION.run_query("""
                    INSERT INTO challengetestgenerator(sid, started, finished, rejected, failed, author, numlanes, numsegments, markings, invalid) VALUES
                    (:sid, :started, :finished, :rejected, :failed, :author, :numLanes, :numSegments, :markings, :invalid)
                    """, gen_stat_args)
                for ai_stat in ai_stats:
                    ai_stat_args = {
                        "sid": ai_stat.sid.sid,
                        "vid": ai_stat.vid.vid,
                        "started": _time_to_string(ai_stat.started),
                        "finished": _time_to_string(ai_stat.finished) if ai_stat.finished else None,
                        "timeout": ai_stat.timeout,
                        "errored": ai_stat.errored,
                        "initialCarToLaneAngle": ai_stat.initial_car_to_lane_angle,
                        "author": ai_name,
                        "notMoving": ai_stat.not_moving,
                        "goalArea": ai_stat.goal_area,
                        "travelledDistance": ai_stat.travelled_distance,
                        "invalidGoalArea": ai_stat.invalid_goal_area
                    }
                    _DB_CONNECTION.run_query("""
                        INSERT INTO challengetestai(sid, vid, started, finished, timeout, errored, initialcartolaneangle, author, notMoving, goalarea, travelleddistance, invalidGoalArea) VALUES
                        (:sid, :vid, :started, :finished, :timeout, :errored, :initialCarToLaneAngle, :author, :notMoving, :goalArea, :travelledDistance, :invalidGoalArea)
                        """, ai_stat_args)


def _do_simple_run(submissions: List[str]) -> None:
    from importlib.util import spec_from_file_location, module_from_spec

    def _process_run_file(name: str, subject: Any) -> None:
        _logger.info("Run sumbission " + name)
        for path in subject:
            spec = spec_from_file_location("submission", path.as_posix())
            module = module_from_spec(spec)
            spec.loader.exec_module(module)

    _do_test_stub({TestType.RUN_FILE: _process_run_file})(submissions)


def _do_ai_scalability(max_num_participants: int) -> None:
    from test_types.ai_scalability_test import ai_scalability_generation, ai_scalability_execution
    ai_scalability_test_paths = ai_scalability_generation(max_num_participants)
    stats = ai_scalability_execution(service, ai_scalability_test_paths)
    for stat in stats:
        args = {
            "sid": stat.sid.sid,
            "numParticipants": stat.num_participants,
            "mode": stat.mode
        }
        _DB_CONNECTION.run_query("""
        INSERT INTO aiscalabilitytest(sid, numparticipants, mode) VALUES
        (:sid, :numParticipants, :mode)
        """, args)


def _do_scalability(num_tests: int, num_nodes: int, round: int) -> None:
    from test_types import get_vids_by_path
    from threading import Thread
    from util import join_all
    from os.path import join, dirname
    submit_threads = []
    ai_threads = []
    executed_sids = []
    for i in range(num_tests):
        def _submit() -> None:
            dbe_path = Path(join(dirname(__file__), "templates", "scalability.dbe.xml"))
            dbc_path = Path(join(dirname(__file__), "templates", "scalability.dbc.xml"))
            submission_result = service.run_tests("test", "test", dbe_path, dbc_path)
            if submission_result and submission_result.submissions:
                _, vids = get_vids_by_path(dbc_path)
                for _, sid in submission_result.submissions.items():
                    executed_sids.append(sid)
                    for vid in vids:
                        ai = ReferenceAI(service)
                        thread = Thread(target=ai.start, args=(sid, vid, lambda: None))
                        thread.daemon = True
                        thread.start()
                        ai_threads.append(thread)

        thread = Thread(target=_submit, args=())
        thread.daemon = True
        thread.start()
        submit_threads.append(thread)

    timeout_threads = join_all(submit_threads, 2 * 60 * 60)
    _logger.info(str(len(timeout_threads)) + " submission threads timed out.")
    timeout_threads = join_all(ai_threads, 2 * 60 * 60)
    _logger.info(str(len(timeout_threads)) + " AI threads timed out.")
    for sid in executed_sids:
        args = {
            "sid": sid.sid,
            "round": round,
            "numNodes": num_nodes
        }
        _DB_CONNECTION.run_query(
            """
            INSERT INTO ScalabilityTest (sid, round, numnodes) VALUES
            (:sid, :round, :numNodes);
            """, args)


@static_vars(generator_stress_time=30, challenge_time=10, challenge_lane_markings=True, ai_stress_max_participants=3,
             scal_num_tests=1, scal_num_nodes=1, scal_round=1)
def _test_submissions(mode: TestMode, submissions: List[str] = None) -> None:
    if not submissions:
        submissions = submission_map.keys()
    _logger.info("Test mode " + mode.name)
    if mode == TestMode.GENERATOR_STRESS:
        _do_generator_stress(submissions, _test_submissions.generator_stress_time)
    elif mode == TestMode.CHALLENGE:
        _do_challenge_test(submissions, _test_submissions.challenge_time, _test_submissions.challenge_lane_markings)
    elif mode == TestMode.SIMPLE_RUN:
        _do_simple_run(submissions)
    elif mode == TestMode.AI_SCALABILITY:
        _do_ai_scalability(_test_submissions.ai_stress_max_participants)
    elif mode == TestMode.SCALABILITY:
        _do_scalability(
            _test_submissions.scal_num_tests, _test_submissions.scal_num_nodes, _test_submissions.scal_round)
    else:
        raise NotImplementedError("TestMode " + str(mode) + " is not implemented, yet.")


if __name__ == "__main__":
    basicConfig(format='%(asctime)s: %(levelname)s - %(message)s', level=WARNING)
    _logger.setLevel(INFO)
    # from test_types.challenge_test import test_ai_against_generator
    # ai = submission_map["Vsevolod Tymofyeyev"][0]
    # generator = submission_map["Sebastian Asen"][0]
    # print(test_ai_against_generator(service, ai, generator, 1))

    _test_submissions(TestMode.CHALLENGE)
    # _test_submissions(TestMode.STRESS)
    # _test_submissions(TestMode.SIMPLE_RUN)
    # _test_submissions(TestMode.SIMPLE_RUN, ["Nguyen Thi Thu Ngan"])

    # _test_submission("Sebastian Vogl")
