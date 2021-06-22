from dataclasses import dataclass
from tkinter import Canvas
from typing import Tuple, List
from xml.dom import minidom
from xml.etree import ElementTree

from drivebuildclient import static_vars
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID, DataResponse

from generateDiagramData import Generator


def _extract_goal_region_definitions() -> None:
    from lxml.etree import fromstring
    result = Generator._run_query(
        """
        SELECT t.criteria
        FROM tests t
            LEFT OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
        WHERE ctg.author = 'Sebastian Asen';
        """
    ).fetchall()
    for criteria in result:
        dbc_tree = fromstring(bytes.fromhex(criteria[0][2:]))
        sc_area_nodes = dbc_tree.xpath("//db:success//db:scArea", namespaces=Generator.NAMESPACES)
        for node in sc_area_nodes:
            print(node.get("points"))


@dataclass
class TraceObject():
    sid: SimulationID
    vid: VehicleID
    tick: int
    response_json: str


def _extract_valid_traces() -> None:
    from google.protobuf.message import DecodeError
    from lxml.etree import fromstring
    from google.protobuf.json_format import MessageToJson
    result = Generator._run_query(
        """
        SELECT t.environment, t.criteria, t.sid, v.tick, v.vid, v.data, t.result, length(v.data)
        FROM tests t 
            FULL OUTER JOIN verificationcycles v ON t.sid = v.sid
        WHERE (t.sid = 1706)
            OR (t.sid = 1709)
        ORDER BY v.tick;
        """
    ).fetchall()
    for environment, criteria, sid, tick, vid, data, result, _ in result:
        response = DataResponse()
        try:
            response.ParseFromString(data)
            with open(str(sid) + "_extracted_traces.json", "a") as f:
                f.write("{\"sid\": " + str(sid)
                        + ",\n\"vid\": \"" + str(vid) + "\""
                        + ",\n\"tick\": " + str(tick)
                        + ",\n\"result\": \"" + str(result) + "\""
                        + ",\n\"trace\": ")
                f.write(MessageToJson(response))
                f.write("}\n")

            def _pretty_print(elem) -> None:
                rough_string = ElementTree.tostring(elem, 'utf-8')
                reparsed = minidom.parseString(rough_string)
                return reparsed.toprettyxml(indent="  ")

            with open(str(sid) + "_environment.dbe.xml", "w") as f:
                f.write(_pretty_print(fromstring(bytes.fromhex(environment[2:]))))
            with open(str(sid) + "_criteria.dbc.xml", "w") as f:
                f.write(_pretty_print(fromstring(bytes.fromhex(criteria[2:]))))
        except DecodeError:
            pass


def _scale_point(point: Tuple[float, float], scale: float) -> Tuple[float, float]:
    return scale * point[0], scale * point[1]


def _translate_lane(lane_points: List[Tuple[float, float]], size: float, move_to_origin: bool = False) \
        -> Tuple[List[Tuple[float, float]], Tuple[float, float]]:
    from shapely.geometry import LineString
    from shapely.affinity import translate, rotate
    from numpy import pi, arctan2
    lane = LineString(lane_points)
    origin_x = size / 2
    if move_to_origin:
        origin_y = size / 4
        delta_y = lane_points[1][1] - lane_points[0][1]
        delta_x = lane_points[1][0] - lane_points[0][0]
        current_angle = arctan2(delta_y, delta_x)
        rotated_lane = rotate(lane, (pi / 2) - current_angle, use_radians=True)
        x, y = rotated_lane.xy
        translated_lane = translate(rotated_lane, origin_x - x[0], origin_y - y[0])
    else:
        origin_y = size / 2
        x, y = lane.xy
        translated_lane = translate(lane, x[0] + origin_x, y[0] + origin_y)
    translated_points: List[Tuple[float, float]] = list(zip(*translated_lane.xy))
    return translated_points, (origin_x, origin_y)


def _split_lanes(lane_points: List[Tuple[float, float]], traveled_distance: float) \
        -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
    from shapely.geometry import Point
    from numpy import arctan2, sin, cos
    remaining_distance = traveled_distance
    traveled_lane_points = [lane_points[0]]
    remaining_lane_points = []
    for i in range(1, len(lane_points)):
        cur = Point(*lane_points[i])
        if remaining_distance < 0:
            remaining_lane_points.append((cur.x, cur.y))
        else:
            prev = Point(*lane_points[i - 1])
            cur_dist = prev.distance(cur)
            if cur_dist <= remaining_distance:
                traveled_lane_points.append((cur.x, cur.y))
            else:
                percentage_length = remaining_distance / cur_dist
                assert percentage_length >= 0, "Percentage length must be non negative"
                if percentage_length == 0:
                    remaining_lane_points.append((prev.x, prev.y))
                else:
                    cur_angle = arctan2(cur.y - prev.y, cur.x - prev.x)
                    part_point = Point(remaining_distance * cos(cur_angle) + prev.x,
                                       remaining_distance * sin(cur_angle) + prev.y)
                    traveled_lane_points.append((part_point.x, part_point.y))
                    remaining_lane_points.append((part_point.x, part_point.y))
            remaining_distance = remaining_distance - cur_dist
    return traveled_lane_points, remaining_lane_points


def _draw_lane(canvas: Canvas, lane_points: List[Tuple[float, float]], color: str = "grey") -> None:
    for i in range(1, len(lane_points)):
        prev = lane_points[i - 1]
        cur = lane_points[i]
        canvas.create_line(prev[0], prev[1], cur[0], cur[1], fill=color)


@static_vars(coo_axis_width=10)
def _add_coo_axis(c: Canvas, axis_length: float) -> None:
    from tkinter import LAST
    coo_axis_offset = 1.5 * _add_coo_axis.coo_axis_width
    arrow_size = 2 * _add_coo_axis.coo_axis_width
    c.create_line(coo_axis_offset,
                  coo_axis_offset,
                  coo_axis_offset + axis_length,
                  coo_axis_offset,
                  fill="black",
                  width=_add_coo_axis.coo_axis_width,
                  arrow=LAST,
                  arrowshape=(arrow_size, arrow_size, coo_axis_offset / 2))
    x_axis_title = c.create_text(coo_axis_offset + axis_length + 10,
                                 coo_axis_offset)
    c.itemconfig(x_axis_title, text="x", font=("Courier New", 20))
    c.create_line(coo_axis_offset,
                  coo_axis_offset,
                  coo_axis_offset,
                  coo_axis_offset + axis_length,
                  fill="black",
                  width=_add_coo_axis.coo_axis_width,
                  arrow=LAST,
                  arrowshape=(arrow_size, arrow_size, coo_axis_offset / 2))
    y_axis_title = c.create_text(coo_axis_offset,
                                 coo_axis_offset + axis_length + 10)
    c.itemconfig(y_axis_title, text="y", font=("Courier New", 20))


@static_vars(scale=2, size=1000, origin_size=8)
def _generate_road_overlay(move_to_origin: bool = False, only_traveled_distance: bool = False) -> None:
    from tkinter import Tk, mainloop
    from lxml.etree import fromstring
    result = Generator._run_query(
        """
        SELECT ctg.author, t.environment, cta.travelleddistance
        FROM tests t
            INNER JOIN challengetestgenerator ctg ON ctg.sid = t.sid
            INNER JOIN challengetestai cta ON t.sid = cta.sid
        WHERE cta.vid = 'ego';
        """
    ).fetchall()
    env_map = {}
    for author, environment, traveled_distance in result:
        if author not in env_map:
            env_map[author] = []
        env_map[author].append((environment, traveled_distance))
    for author in env_map.keys():
        master = Tk()
        master.title("Roads of " + author)
        master.configure(background="black")
        c = Canvas(master, width=_generate_road_overlay.size, height=_generate_road_overlay.size)
        c.configure(background="white")
        c.pack()
        for environment, traveled_distance in env_map[author]:
            dbe_tree = fromstring(bytes.fromhex(environment[2:]))
            for lane_node in dbe_tree.xpath("//db:lane", namespaces=Generator.NAMESPACES):
                lane_segment_nodes = lane_node.xpath("db:laneSegment", namespaces=Generator.NAMESPACES)
                scaled_points = [_scale_point(
                    (float(l.get("x")), float(l.get("y"))),
                    _generate_road_overlay.scale
                ) for l in lane_segment_nodes]
                translated_lane, origin = _translate_lane(scaled_points, _generate_road_overlay.size, move_to_origin)

                if only_traveled_distance:
                    traveled_lane, remaining_lane = \
                        _split_lanes(translated_lane, traveled_distance)
                    _draw_lane(c, traveled_lane, "green")
                    # _draw_lane(c, remaining_lane, "red")
                else:
                    _draw_lane(c, translated_lane)
            c.create_oval(origin[0] - _generate_road_overlay.origin_size,
                          origin[1] - _generate_road_overlay.origin_size,
                          origin[0] + _generate_road_overlay.origin_size,
                          origin[1] + _generate_road_overlay.origin_size,
                          fill="red",
                          outline="red")
            axis_length = _generate_road_overlay.size / 5
            _add_coo_axis(c, axis_length)
        mainloop()


if __name__ == "__main__":
    _generate_road_overlay(move_to_origin=False, only_traveled_distance=False)
    _generate_road_overlay(move_to_origin=True, only_traveled_distance=False)
    _generate_road_overlay(move_to_origin=True, only_traveled_distance=True)
