from logging import getLogger

from drivebuildclient.aiExchangeMessages_pb2 import VehicleID
from lxml.etree import _ElementTree, Element, _Element
from pathlib import Path
from shapely.geometry import Point
from typing import Optional, Tuple, List, Dict

_logger = getLogger("SubmissionTester.TestTypes")


def get_vids_by_path(path: Path) -> Optional[Tuple[str, List[VehicleID]]]:
    from xml_util import parse_xml
    dbc_tree = parse_xml(path)
    return get_vids_by_tree(dbc_tree)


def get_vids_by_tree(dbc_tree: _ElementTree) -> Optional[Tuple[str, List[VehicleID]]]:
    from util import is_dbc
    from xml_util import findall, find
    if is_dbc(dbc_tree):
        participant_nodes = findall(dbc_tree, "//db:participant")
        test_name = find(dbc_tree, "//db:name").text
        vids = []
        for participant_node in participant_nodes:
            vid = VehicleID()
            vid.vid = participant_node.get("id")
            vids.append(vid)
        return test_name, vids
    else:
        return None


def get_all_vids_by_path(paths: List[Path]) -> Dict[str, List[VehicleID]]:
    from xml_util import parse_xml
    return get_all_vids_by_tree([parse_xml(path) for path in paths])


def get_all_vids_by_tree(trees: List[_ElementTree]) -> Dict[str, List[VehicleID]]:
    all_vids = {}
    for tree in trees:
        vids = get_vids_by_tree(tree)
        if vids:
            if vids[0] in all_vids:
                _logger.warning("The DBCs extracting VehicleIDs from contain duplicate test names. "
                                "The output of this function will not contain both.")
            all_vids[vids[0]] = vids[1]
    return all_vids


def _get_points_of_goal_area(node: _Element) -> List[Tuple[float, float]]:
    serialized_points = node.get("points")
    points = []
    for point_tuple in serialized_points.split(";"):
        coos = point_tuple[1:-1].split(",")
        points.append((float(coos[0]), float(coos[1])))
    return points


def determine_target_positions(dbe_tree: _ElementTree, dbc_tree: _ElementTree) \
        -> Dict[str, Tuple[Optional[Point], bool]]:
    from xml_util import findall, find
    from shapely.geometry import Polygon
    candidates = {}
    participant_nodes = findall(dbc_tree, "//db:participant")
    for participant_node in participant_nodes:
        participant_id = participant_node.get("id")
        candidate = None
        invalid_goal_area = False

        def _get_last_waypoint() -> Optional[Point]:
            last_waypoint = None
            movement_node = find(participant_node, "db:movement")
            if movement_node is not None:
                waypoint_nodes = movement_node.getchildren()
                if waypoint_nodes:
                    last_waypoint = Point(float(waypoint_nodes[-1].get("x")), float(waypoint_nodes[-1].get("y")))
            return last_waypoint

        # FIXME Consider conjunctions and disjunctions of criteria?
        # FIXME Support multiple participants with multiple goal regions?
        goal_position_nodes = list(
            filter(
                lambda n: n.get("participant") == participant_id,
                findall(dbc_tree, "//db:success//db:scPosition")
            )
        )
        num_goal_positions = len(goal_position_nodes)
        if num_goal_positions <= 0:
            # FIXME Exclude negated scArea in success
            # FIXME Include negated scArea in failure
            goal_region_nodes = list(
                filter(
                    lambda n: n.get("participant") == participant_id,
                    findall(dbc_tree, "//db:success//db:scArea")
                )
            )
            num_goal_regions = len(goal_region_nodes)
            if num_goal_regions <= 0:
                _logger.debug("The test associates no goal region and no goal position with the participant. "
                              "Choose last waypoint.")
                candidate = _get_last_waypoint()
                invalid_goal_area = True
            elif num_goal_regions == 1:
                # Determine new target waypoint
                goal_area = Polygon(shell=_get_points_of_goal_area(goal_region_nodes[0]))
                lane_segment_points = map(
                    lambda n: Point(float(n.get("x")), float(n.get("y"))), findall(dbe_tree, "//db:laneSegment")
                )
                candidate_segment_points = list(filter(lambda p: goal_area.contains(p), lane_segment_points))
                if candidate_segment_points:
                    candidate = candidate_segment_points[0]
                else:
                    _logger.debug("Could not find a lane center point that intersects with the goal region. "
                                  "Choose last lane center point.")
                    candidate = _get_last_waypoint()
                    invalid_goal_area = True
            else:
                _logger.debug(
                    "Can not determine candidate since there is no goal position but more than one goal region")
        elif num_goal_positions == 1:
            candidate = Point(float(goal_position_nodes[0].get("x")),
                              float(goal_position_nodes[0].get("y")))
        else:
            _logger.debug(
                "Can not determine candidate since there are multiple goal positions associated with the participant.")
        candidates[participant_id] = (candidate, invalid_goal_area)
    return candidates


def set_target_position(participant_node: _Element, target_position: Point) -> None:
    from xml_util import find, findall
    # Remove all waypoints
    movement_node = find(participant_node, "db:movement")
    if movement_node is None:
        movement_node = Element("movement")
        participant_node.append(movement_node)
    else:
        waypoint_nodes = findall(movement_node, "db:waypoint")
        for waypoint_node in waypoint_nodes:
            movement_node.remove(waypoint_node)
    # Add new target waypoint
    target_waypoint_node = Element("waypoint")
    target_waypoint_node.set("x", str(target_position.x))
    target_waypoint_node.set("y", str(target_position.y))
    target_waypoint_node.set("tolerance", "1")  # FIXME Choose proper tolerance
    target_waypoint_node.set("movementMode", "_BEAMNG")
    movement_node.append(target_waypoint_node)


def extend_goal_region(dbc_tree: _ElementTree, participant_id: str, goal_position: Point) -> None:
    from xml_util import find
    success_node = find(dbc_tree, "//db:success")
    success_criterion_nodes = success_node.getchildren()
    success_node.clear()
    or_tag = Element("or")
    or_tag.extend(success_criterion_nodes)
    goal_position_node = Element("scPosition")
    goal_position_node.set("participant", participant_id)
    goal_position_node.set("x", str(goal_position.x))
    goal_position_node.set("y", str(goal_position.y))
    goal_position_node.set("tolerance", "3")  # FIXME Determine a sophisticated value
    or_tag.append(goal_position_node)
    success_node.append(or_tag)


def set_failure_tag(dbc_tree: _ElementTree) -> None:
    from xml_util import find
    # Fill empty failure tags
    failure_node = find(dbc_tree, "//db:failure")
    for criterion in failure_node.getchildren():
        failure_node.remove(criterion)
    if not failure_node.getchildren():
        or_tag = Element("or")
        _, vids = get_vids_by_tree(dbc_tree)
        for vid in vids:
            damage_tag = Element("scDamage")
            damage_tag.set("participant", vid.vid)
            or_tag.append(damage_tag)
            offroad_tag = Element("scLane")
            offroad_tag.set("participant", vid.vid)
            offroad_tag.set("onLane", "offroad")
            or_tag.append(offroad_tag)
        failure_node.append(or_tag)
