from logging import getLogger

from dataclasses import dataclass, field
from datetime import datetime
from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID
from drivebuildclient import static_vars
from lxml.etree import _ElementTree
from pathlib import Path
from typing import Any, Tuple, List, Optional, Dict


@dataclass
class ChallengeTestStat():
    sid: SimulationID = None
    started: datetime = None
    finished: Optional[datetime] = None


@dataclass
class ChallengeTestGeneratorStat(ChallengeTestStat):
    failed: bool = False
    rejected: bool = False  # FIXME Leave it in since (sid => not rejected)?
    num_lanes: int = None
    invalid: bool = False
    num_segments: List[int] = field(default_factory=list)
    markings: List[bool] = field(default_factory=list)


@dataclass
class ChallengeTestAIStat(ChallengeTestStat):
    vid: VehicleID = None
    errored: bool = False
    timeout: bool = False
    initial_car_to_lane_angle: float = None
    goal_area: float = None
    not_moving: bool = False
    travelled_distance: float = 0
    invalid_goal_area: bool = False


_logger = getLogger("SubmissionTester.TestTypes.ChallengeTest")


def _prepare_test_files(dbe_tree: _ElementTree, dbc_tree: _ElementTree, ai: Any, lane_markings: Optional[bool]) \
        -> Dict[str, ChallengeTestAIStat]:
    from xml_util import find, findall
    from lxml.etree import Element
    from test_types import set_failure_tag, determine_target_positions, set_target_position, extend_goal_region
    from reference.ai import ReferenceAI
    # TODO Fix aiFrequencey and stepsPerSecond
    # Enforce movement modes
    ego_movement_mode_nodes = findall(dbc_tree, "//db:participant[@id='ego']//*[@movementMode]")
    if isinstance(ai, ReferenceAI):
        enforced_mode = "_BEAMNG"
        target_positions = determine_target_positions(dbe_tree, dbc_tree)
    else:
        enforced_mode = "AUTONOMOUS"
        target_positions = None
    for node in ego_movement_mode_nodes:
        node.set("movementMode", enforced_mode)
    non_ego_movement_mode_nodes = findall(dbc_tree, "//db:participant[@id!='ego']//*[@movementMode='AUTONOMOUS']")
    for node in non_ego_movement_mode_nodes:
        node.set("movementMode", "TRAINING")

    # Possibly enforce lane markings
    if lane_markings is not None:
        lane_nodes = findall(dbe_tree, "//db:lane")
        for node in lane_nodes:
            node.set("markings", "true" if lane_markings else "false")

    participant_nodes = findall(dbc_tree, "//db:participant")
    ai_stats = {}
    for participant_node in participant_nodes:
        ai_stat = ChallengeTestAIStat()
        # Add data requests required by the AI to all participants
        data_request_node = find(participant_node, "db:ai")
        if data_request_node is None:
            data_request_node = Element("ai")
            participant_node.append(data_request_node)
        participant_id = participant_node.get("id")
        ai.add_data_requests(data_request_node, participant_id)
        submission_car_to_lane_request = Element("carToLaneAngle")
        submission_car_to_lane_request.set("id", "submissionCarToLane_" + participant_id)
        data_request_node.append(submission_car_to_lane_request)
        submission_position_request = Element("position")
        submission_position_request.set("id", "submissionPosition_" + participant_id)
        data_request_node.append(submission_position_request)
        # In case of the movement mode _BEAMNG set the target position for the AV
        if target_positions:
            target_position, ai_stat.invalid_goal_area = target_positions[participant_id]
            if target_position:
                set_target_position(participant_node, target_position)
                extend_goal_region(dbc_tree, participant_id, target_position)
        ai_stats[participant_id] = ai_stat

    set_failure_tag(dbc_tree)
    return ai_stats


def _generate_test_files(generator: Any, ai: Any, lane_markings: Optional[bool]) \
        -> Tuple[Optional[Path], Optional[Path], ChallengeTestGeneratorStat, Dict[str, ChallengeTestAIStat]]:
    from util import is_dbc, is_dbe
    from xml_util import parse_xml, find
    from util import silence_stdout
    from os.path import basename
    from lxml.etree import tostring
    ai_stats = {}
    dbe_path = None
    dbc_path = None
    gen_stat = ChallengeTestGeneratorStat()
    with silence_stdout():
        try:
            gen_stat.started = datetime.now()
            test = generator.getTest()
            if test:
                dbe_path, dbc_path = test
            else:
                gen_stat.failed = True
        except Exception as ex:
            _logger.exception(ex)
            gen_stat.failed = True
        finally:
            gen_stat.finished = datetime.now()
    if not gen_stat.failed:
        dbe_tree = parse_xml(dbe_path)
        if not is_dbe(dbe_tree):
            _logger.debug("\"" + dbe_path.as_posix() + "\" is not a DBE.")
            gen_stat.invalid = True
        dbc_tree = parse_xml(dbc_path)
        if is_dbc(dbc_tree):
            associated_dbe = find(dbc_tree, "//db:environment").text.strip()
            if associated_dbe != basename(dbe_path):
                _logger.debug("The DBC \"" + dbc_path.as_posix() + "\" does not reference the generated DBE.")
                gen_stat.invalid = True
        else:
            _logger.debug("\"" + dbc_path.as_posix() + "\" is not a DBC.")
            gen_stat.invalid = True
        if not gen_stat.invalid:
            ai_stats = _prepare_test_files(dbe_tree, dbc_tree, ai, lane_markings)
            with open(dbe_path.as_posix(), "wb") as out_file:
                out_file.write(tostring(dbe_tree))
            with open(dbc_path.as_posix(), "wb") as out_file:
                out_file.write(tostring(dbc_tree))
    return dbe_path, dbc_path, gen_stat, ai_stats


def _check_validity_constraints(dbe_tree: _ElementTree, dbc_tree: _ElementTree, gen_stat: ChallengeTestGeneratorStat) \
        -> None:
    from xml_util import find
    if find(dbc_tree, "//db:participant[@id='ego']") is None:
        gen_stat.invalid = True


@static_vars(min_distance=5, min_position_records=5, min_movement_time=60)
def _handle_ai(service: AIExchangeService, ai: Any, sid: SimulationID, vid: VehicleID,
               ai_stat: ChallengeTestAIStat) -> None:
    from drivebuildclient.aiExchangeMessages_pb2 import DataRequest, TestResult
    from util import silence_stdout
    from shapely.geometry import Point
    from exceptions import NotMovingTermination, Termination
    position_records: List[Point] = []

    def _add_dynamic_stats() -> None:
        request = DataRequest()
        request.request_ids.extend([
            "submissionCarToLane_" + vid.vid,
            "submissionPosition_" + vid.vid
        ])
        data = service.request_data(sid, vid, request)
        if data:
            if not ai_stat.initial_car_to_lane_angle:
                # Initial car-to-lane-angle
                if "submissionCarToLane_" + vid.vid in data.data:
                    ai_stat.initial_car_to_lane_angle \
                        = data.data["submissionCarToLane_" + vid.vid].car_to_lane_angle.angle
            # No-movement detection
            if "submissionPosition_" + vid.vid in data.data:
                current_position = data.data["submissionPosition_" + vid.vid].position
                position_records.append(Point(current_position.x, current_position.y))
                if len(position_records) > 1:
                    previous_point = position_records[-2]
                    current_point = position_records[-1]
                    ai_stat.travelled_distance = ai_stat.travelled_distance + previous_point.distance(current_point)
                if len(position_records) > _handle_ai.min_position_records \
                        and (datetime.now() - ai_stat.started).seconds > _handle_ai.min_movement_time \
                        and ai_stat.travelled_distance < _handle_ai.min_distance:
                    ai_stat.not_moving = True
                    raise NotMovingTermination()

    try:
        with silence_stdout():
            ai_stat.started = datetime.now()
            try:
                ai.start(sid, vid, _add_dynamic_stats)
            except Termination as ex:
                _logger.debug("Detected termination signal (" + str(ex) + ") for AI " + vid.vid + ".")
                result = TestResult()
                result.result = TestResult.Result.SKIPPED
                service.control_sim(sid, result)
    except Exception as ex:
        _logger.debug("The AI implementation encountered an internal error.")
        _logger.exception(str(ex))
        ai_stat.errored = True
    finally:
        ai_stat.finished = datetime.now()


def _get_dbc_with_name(test_trees: List[_ElementTree], test_name: str) -> Optional[_ElementTree]:
    from util import is_dbc
    from xml_util import find
    dbc_tree = None
    for tree in test_trees:
        if is_dbc(tree) and find(tree, "//db:name").text == test_name:
            dbc_tree = tree
            break
    return dbc_tree


def _calculate_goal_area(criteria_tree: _ElementTree, vid: VehicleID) -> float:
    from xml_util import findall
    from shapely.geometry import Point, Polygon
    from reference.generator import ReferenceTestGenerator
    from shapely.ops import cascaded_union
    # FIXME Does not recognize any negated nodes in success criterion
    # FIXME Does not recognize any negated nodes in failure criterion
    # FIXME Does not calculate the intersection with lanes
    goal_position_nodes = findall(criteria_tree, "//db:success//db:scPosition[@participant='" + vid.vid + "']")
    goal_area_shapes = list(map(
        lambda n: Point(float(n.get("x")), float(n.get("y"))).buffer(float(n.get("tolerance"))),
        goal_position_nodes
    ))
    goal_area_nodes = findall(criteria_tree, "//db:success//db:scArea[@participant='" + vid.vid + "']")
    goal_area_shapes.extend(list(map(
        lambda n: Polygon(shell=ReferenceTestGenerator.get_points_of_goal_area(n)),
        goal_area_nodes
    )))
    return cascaded_union(goal_area_shapes).area


def _run_fight(service: AIExchangeService, generator: Any, ai: Any, lane_markings: Optional[bool]) \
        -> Tuple[ChallengeTestGeneratorStat, List[ChallengeTestAIStat]]:
    from threading import Thread
    from os import remove
    from util import join_all
    from test_types import get_vids_by_tree
    from xml_util import parse_xml, findall
    from reference.ai import ReferenceAI
    dbe_path, dbc_path, gen_stat, ai_stats = _generate_test_files(generator, ai, lane_markings)
    # NOTE Assumes that the test file paths contain only one test
    if not gen_stat.failed and not gen_stat.invalid \
            and dbe_path is not None and dbc_path is not None:
        dbe_tree = parse_xml(dbe_path)
        dbc_tree = parse_xml(dbc_path)
        _check_validity_constraints(dbe_tree, dbc_tree, gen_stat)
        submission_result = service.run_tests("test", "test", dbe_path, dbc_path)
        if submission_result and submission_result.submissions:
            _, vids = get_vids_by_tree(dbc_tree)
            ai_threads = {}
            for _, sid in submission_result.submissions.items():
                gen_stat.sid = sid
                lane_nodes = findall(dbe_tree, "//db:lane")
                gen_stat.num_lanes = len(lane_nodes)
                gen_stat.num_segments.extend([len(findall(n, "db:laneSegment")) for n in lane_nodes])
                gen_stat.markings.extend([n.get("markings", "false") == "true" for n in findall(dbe_tree, "//db:lane")])
                for vid in vids:
                    ai_stat = ai_stats[vid.vid]
                    ai_stat.sid = sid
                    ai_stat.vid = vid
                    ai_stat.goal_area = _calculate_goal_area(dbc_tree, vid)
                    thread = Thread(target=_handle_ai,
                                    args=(service, ai if vid.vid == "ego" else ReferenceAI(service), sid, vid, ai_stat))
                    thread.start()
                    ai_threads[vid.vid] = thread
            # NOTE Set to a slightly bigger value than the simulation timeout value in DriveBuild
            timeout_threads = join_all(list(ai_threads.values()), 11 * 60)
            for vid, thread in ai_threads.items():
                if thread in timeout_threads:
                    _logger.debug("AI timed out.")
                    ai_stats[vid].timeout = True
        else:
            _logger.debug("The generator failed or DriveBuild rejected all the generated tests")
            gen_stat.rejected = submission_result is None or submission_result.submissions is None

    # Remove generated test files
    if dbe_path:
        remove(dbe_path.as_posix())
    if dbc_path:
        remove(dbc_path.as_posix())
    return gen_stat, list(ai_stats.values())


def test_ai_against_generator(service: AIExchangeService, generator: Any, ai: Any, time: int,
                              lane_markings: Optional[bool] = None) \
        -> List[Tuple[ChallengeTestGeneratorStat, Optional[List[ChallengeTestAIStat]]]]:
    from threading import Thread
    continue_challenge = True
    stats = []

    def _run_fights() -> None:
        while continue_challenge:
            stats.append(_run_fight(service, generator, ai, lane_markings))

    challenge_process = Thread(target=_run_fights)
    challenge_process.daemon = True
    challenge_process.start()
    challenge_process.join(time * 60)
    continue_challenge = False
    challenge_process.join()

    return stats
