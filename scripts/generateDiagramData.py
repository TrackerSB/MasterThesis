from os.path import join, dirname
from pathlib import Path
from typing import Optional, Any, Dict, List, Union

from pg8000 import Cursor


class Generator:
    _output_dir = Path(join(dirname(__file__), "generatedData"))
    NAMESPACES = {
        "db": "http://drivebuild.com"
    }

    @staticmethod
    def _run_query(query: str, args: Dict[str, Any] = None) -> Cursor:
        from pg8000 import connect
        import pg8000
        pg8000.paramstyle = "named"
        with connect(host="localhost",
                     port=5432,
                     database="masterthesis",
                     user="stefan",
                     password="stefan") as connection:
            connection.autocommit = True
            with connection.cursor() as cursor:
                return cursor.execute(query, args)

    @staticmethod
    def _get_headings(data: Cursor) -> List[str]:
        return [d[0].decode() for d in data.description]

    @staticmethod
    def _export_diagram_data(filename: str, data: Union[Cursor, List[List[Any]]]) -> None:
        from csv import writer, excel
        with open(join(Generator._output_dir.as_posix(), filename), "w") as file:
            csv_writer = writer(file, dialect=excel)
            if isinstance(data, Cursor):
                csv_writer.writerow(Generator._get_headings(data))
                csv_writer.writerows(data.fetchall())
            else:
                csv_writer.writerows(data)

    @staticmethod
    def diagram_1() -> None:
        """
        Influence of markings to travelled distance
        """
        Generator._export_diagram_data(
            "diagram1.csv",
            Generator._run_query(
                """
                SELECT cta.author,
                       array_avg(ctg.markings) AS allMarkings,
                       cta.travelleddistance
                FROM tests t
                         FULL OUTER JOIN challengetestai cta ON t.sid = cta.sid
                         FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                WHERE cta.author IS NOT NULL
                  AND NOT ctg.failed
                  AND NOT ctg.invalid
                  AND NOT cta.errored
                GROUP BY cta.author, allMarkings, cta.travelleddistance
                ORDER BY cta.author, allMarkings;   
                """
            )
        )

    @staticmethod
    def diagram_2() -> None:
        """
        With which generator can AIs cope the best?
        """
        Generator._export_diagram_data(
            "diagram2.csv",
            Generator._run_query(
                """
                SELECT ctg.author AS generatorAuthor, cta.author AS aiAuthor, cta.travelleddistance
                FROM tests t
                         FULL OUTER JOIN challengetestai cta ON t.sid = cta.sid
                         FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                WHERE cta.author IS NOT NULL
                  AND NOT ctg.failed
                  AND NOT ctg.invalid
                GROUP BY ctg.author, cta.travelleddistance, cta.author;
                """
            )
        )

    @staticmethod
    def diagram_3() -> None:
        """
        Placement of vehicles in generated tests
        """
        Generator._export_diagram_data(
            "diagram3.csv",
            Generator._run_query(
                """
                SELECT ctg.author, cta.initialcartolaneangle, cta.travelleddistance
                FROM tests t
                         FULL OUTER JOIN challengetestai cta ON t.sid = cta.sid
                         FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                WHERE cta.author IS NOT NULL
                  AND NOT ctg.failed
                  AND NOT ctg.invalid
                GROUP BY ctg.author, cta.initialcartolaneangle, cta.travelleddistance;
                """
            )
        )

    @staticmethod
    def diagram_4() -> None:
        """
        Successful, failing tests and invalid tests
        """
        Generator._export_diagram_data(
            "diagram4.csv",
            Generator._run_query(
                """
                SELECT ctg.author AS generatorAuthor,
                    cta.author AS aiAuthor,
                    t.result,
                    t.status, count(*) AS number,
                    ctg.invalid,
                    ctg.failed
                FROM tests t
                    FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                    FULL OUTER JOIN challengetestai cta ON t.sid = cta.sid
                GROUP BY ctg.author, cta.author, t.result, t.status, ctg.invalid, ctg.failed;
                """
            )
        )

    @staticmethod
    def diagram_5() -> None:
        """
        Test Generator: Efficiency/Effectiveness
        """
        Generator._export_diagram_data(
            "diagram5.csv",
            Generator._run_query(
                """
                SELECT ctg.author, ctg.invalid AS rejected, ctg.failed, count(*) AS number
                FROM challengetestgenerator ctg
                GROUP BY ctg.author, ctg.invalid, ctg.failed;
                """
            )
        )

    @staticmethod
    def diagram_6() -> None:
        """
        Test Cases: Effectiveness
        """
        Generator._export_diagram_data(
            "diagram6.csv",
            Generator._run_query(
                """
                SELECT ctg.author, t.result, count(*) AS number
                FROM tests t
                    FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                WHERE t.status = 'FINISHED'
                GROUP BY ctg.author, t.result
                UNION ALL
                SELECT ctg2.author, 'TIMEOUT', count(*)
                FROM tests t2
                    FULL OUTER JOIN challengetestgenerator ctg2 ON t2.sid = ctg2.sid
                WHERE t2.status = 'TIMEOUT'
                GROUP BY ctg2.author, t2.result;
                """
            )
        )

    #     data_record = Generator._run_query(
    #         """
    #         SELECT t.sid, t.environment, t.result, t.status, v.tick, v.data
    #         FROM tests t
    #         LEFT OUTER JOIN verificationcycles v ON t.sid = v.sid;
    #         """
    #     ).fetchall()
    #     diagram_data = {}
    #     for sid, environment, result, status, tick, data in data_record:
    #         if result == "FAILED":
    #             diagram_data[sid] = "FAILED"
    #             if sid not in diagram_data or diagram_data[sid] == "DAMAGED":
    #                 dbe_tree = fromstring(bytes.fromhex(environment[2:]))
    #                 lane_lines = []
    #                 for lane_node in dbe_tree.xpath("//db:lane", namespaces=Generator.NAMESPACES):
    #                     lane_segment_nodes = lane_node.xpath("db:laneSegment", namespaces=Generator.NAMESPACES)
    #                     lane_line = LineString([(float(n.get("x")), float(n.get("y"))) for n in lane_segment_nodes])
    #                     lane_width = float(lane_segment_nodes[0].get("width"))
    #                     lane_lines.append((lane_line, lane_width))
    #                 print(len(data))
    #                 trace_entry = DataResponse()
    #                 try:
    #                     trace_entry.ParseFromString(data)
    #                     for _, data_entry in trace_entry.data.items():
    #                         if data_entry.HasField("bounding_box"):
    #                             current_position = data_entry.bounding_box
    #                             break
    #                     else:
    #                         current_position = None
    #                     bounding_box_positions = zip(current_position.points[0::2], current_position.points[1::2])
    #                     bounding_box = Polygon(shell=bounding_box_positions)
    #                     if any([lane_line.distance(bounding_box) < (width / 2) for lane_line, width in lane_lines]):
    #                         diagram_data[sid] = "DAMAGED"
    #                     else:
    #                         diagram_data[sid] = "OFFROAD"
    #                 except Exception:
    #                     print("Decoding failed")
    #         else:
    #             if sid not in diagram_data:
    #                 if result == "UNKNOWN":
    #                     if status == "TIMEOUT":
    #                         diagram_data[sid] = "TIMEOUT"
    #                     else:
    #                         print("Diagram6 evaluation can not handle result UNKNOWN combined with status "
    #                               + str(status))
    #                 elif result == "SUCCEEDED":
    #                     diagram_data[sid] = "SUCCEEDED"
    #                 else:
    #                     print("Diagram6 evaluation can not handle result " + str(result))
    #     output_data = [["sid", "result"]]
    #     output_data.extend([[sid, result] for sid, result in diagram_data.items()])
    #     Generator._export_diagram_data(
    #         "diagram6.csv",
    #         output_data
    #     )

    @staticmethod
    def diagram_7() -> None:
        """
        Test Cases: Complexity: Number of segments
        """
        from lxml.etree import fromstring
        result = Generator._run_query(
            """
            SELECT t.environment, ctg.author
            FROM tests t
                FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
            WHERE NOT ctg.failed;
            """
        ).fetchall()
        output_data = [["author", "numsegments"]]
        for environment, author in result:
            dbe_tree = fromstring(bytes.fromhex(environment[2:]))
            for lane_node in dbe_tree.xpath("//db:lane", namespaces=Generator.NAMESPACES):
                num_segments = len(lane_node.xpath("db:laneSegment", namespaces=Generator.NAMESPACES))
                output_data.append([author, num_segments])
        Generator._export_diagram_data(
            "diagram7.csv",
            output_data
        )

    @staticmethod
    def diagram_8() -> None:
        """
        Test Cases: Complexity: Road length
        """
        from lxml.etree import fromstring
        from shapely.geometry import LineString
        result = Generator._run_query(
            """
            SELECT t.environment, ctg.author
            FROM tests t
                FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
            WHERE NOT ctg.failed;
            """
        ).fetchall()
        output_data = [["author", "roadlength"]]
        for environment, author in result:
            dbe_tree = fromstring(bytes.fromhex(environment[2:]))
            for lane_node in dbe_tree.xpath("//db:lane", namespaces=Generator.NAMESPACES):
                lane_segment_nodes = lane_node.xpath("db:laneSegment", namespaces=Generator.NAMESPACES)
                lane_line = LineString([(float(n.get("x")), float(n.get("y"))) for n in lane_segment_nodes])
                output_data.append([author, lane_line.length])
        Generator._export_diagram_data(
            "diagram8.csv",
            output_data
        )

    @staticmethod
    def diagram_9() -> None:
        """
        Test Cases: Complexity: Number of roads
        """
        from lxml.etree import fromstring
        result = Generator._run_query(
            """
            SELECT t.environment, ctg.author
            FROM tests t
                FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
            WHERE NOT ctg.failed;
            """
        ).fetchall()
        output_data = [["author", "numroads"]]
        for environment, author in result:
            dbe_tree = fromstring(bytes.fromhex(environment[2:]))
            num_participants = len(dbe_tree.xpath("//db:lane", namespaces=Generator.NAMESPACES))
            output_data.append([author, num_participants])
        Generator._export_diagram_data(
            "diagram9.csv",
            output_data
        )

    @staticmethod
    def diagram_10() -> None:
        """
        Test Cases: Complexity: Number of obstacles
        """
        from lxml.etree import fromstring
        result = Generator._run_query(
            """
            SELECT t.environment, ctg.author
            FROM tests t
                FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
            WHERE NOT ctg.failed;
            """
        ).fetchall()
        output_data = [["author", "numobstacles"]]
        for environment, author in result:
            dbe_tree = fromstring(bytes.fromhex(environment[2:]))
            obstacles_node = dbe_tree.xpath("//db:obstacles", namespaces=Generator.NAMESPACES)
            num_obsatcles = 0 if obstacles_node is None or len(obstacles_node) < 1 \
                else len(obstacles_node[0].getchildren())
            output_data.append([author, num_obsatcles])
        Generator._export_diagram_data(
            "diagram10.csv",
            output_data
        )

    @staticmethod
    def diagram_11() -> None:
        """
        Test Cases: Complexity: Number of participants
        """
        from lxml.etree import fromstring
        result = Generator._run_query(
            """
            SELECT t.criteria, ctg.author
            FROM tests t
                FULL OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
            WHERE NOT ctg.failed;
            """
        ).fetchall()
        output_data = [["author", "numparticipants"]]
        for criteria, author in result:
            dbc_tree = fromstring(bytes.fromhex(criteria[2:]))
            num_participants = len(dbc_tree.xpath("//db:participant", namespaces=Generator.NAMESPACES))
            output_data.append([author, num_participants])
        Generator._export_diagram_data(
            "diagram11.csv",
            output_data
        )

    @staticmethod
    def diagram_12() -> None:
        """
        How many tests failed, succeeded, errored,... per challenge round?
        """
        Generator._export_diagram_data(
            "diagram12.csv",
            Generator._run_query(
                """
                SELECT ctg.round, ctg.author AS genAuthor, cta.author AS aiAuthor, t.result, t.status, ctg.invalid,
                    ctg.failed, cta.errored AS aiErrored
                FROM tests t
                    RIGHT OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                    FULL OUTER JOIN challengetestai cta ON t.sid = cta.sid
                WHERE (cta.vid = 'ego'
                    OR cta.vid IS NULL)
                    AND (NOT cta.notmoving OR cta.errored OR ctg.failed)
                UNION ALL
                SELECT ctg.round, ctg.author, cta.author, 'NOT MOVING', 'CANCELED', ctg.invalid, ctg.failed, cta.errored
                FROM tests t
                    RIGHT OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid
                    FULL OUTER JOIN challengetestai cta ON t.sid = cta.sid
                WHERE (cta.vid = 'ego'
                    OR cta.vid IS NULL)
                    AND cta.notmoving;
                """)
        )

    @staticmethod
    def diagram_13() -> None:
        """
        Investigate goal areas.
        """
        Generator._export_diagram_data(
            "diagram13.csv",
            Generator._run_query(
                """
                SELECT cta.goalarea, cta.invalidgoalarea, ctg.author
                FROM challengetestai cta
                    LEFT OUTER JOIN challengetestgenerator ctg ON cta.sid = ctg.sid;
                """
            )
        )

    @staticmethod
    def diagram_14() -> None:
        """
        Invest execution times of AIs.
        """
        Generator._export_diagram_data(
            "diagram14.csv",
            Generator._run_query(
                """
                SELECT cta.author AS aiAuthor, cta.started, cta.finished,ctg.author AS genAuthor
                FROM challengetestai cta
                    LEFT OUTER JOIN challengetestgenerator ctg ON cta.sid = ctg.sid
                    LEFT OUTER JOIN tests t ON cta.sid = t.sid
                WHERE NOT cta.errored
                    AND NOT cta.timeout
                    AND NOT t.status = 'TIMEOUT'
                    AND NOT cta.invalidgoalarea;
                """
            )
        )

    @staticmethod
    def diagram_15() -> None:
        """
        Invest execution times of test generators.
        """
        Generator._export_diagram_data(
            "diagram15.csv",
            Generator._run_query(
                """
                SELECT ctg.author, ctg.started, ctg.finished
                FROM challengetestgenerator ctg;
                """
            )
        )

    @staticmethod
    def diagram_16() -> None:
        """
        Number generated tests per round and time budget.
        """
        Generator._export_diagram_data(
            "diagram16.csv",
            Generator._run_query(
                """
                SELECT ctg.author, ctg.round, count(*) AS number, CASE WHEN ctg.round < 5 THEN 10 ELSE 30 END AS budget
                FROM challengetestgenerator ctg
                GROUP BY ctg.author, ctg.round;
                """
            )
        )

    @staticmethod
    def diagram_17() -> None:
        """
        Invest execution times of simulations.
        """
        Generator._export_diagram_data(
            "diagram17.csv",
            Generator._run_query(
                """
                SELECT ctg.author, t.started, t.finished
                FROM tests t
                    LEFT OUTER JOIN challengetestgenerator ctg ON t.sid = ctg.sid;
                """
            )
        )

    @staticmethod
    def diagram_18() -> None:
        """
        Output scalability test data
        NOTE It uses the same table as diagram_19. => Make sure it contains the right entries
        """
        Generator._export_diagram_data(
            "diagram18.csv",
            Generator._run_query(
                """
                SELECT s.round, s.numnodes, t.result, t.status, t.started, t.finished
                FROM scalabilitytest s
                    LEFT OUTER JOIN tests t ON s.sid = t.sid
                ORDER BY s.round;
                """
            )
        )

    @staticmethod
    def diagram_19() -> None:
        """
        Output scalability test data for laptop
        NOTE It uses the same table as diagram_18. => Make sure it contains the right entries
        """
        Generator._export_diagram_data(
            "diagram19.csv",
            Generator._run_query(
                """
                SELECT s.round, s.numnodes, t.result, t.status, t.started, t.finished
                FROM scalabilitytest s
                    LEFT OUTER JOIN tests t ON s.sid = t.sid
                ORDER BY s.round;
                """
            )
        )

    @staticmethod
    def diagram_20() -> None:
        """
        Time for running x tests at once
        """
        Generator._export_diagram_data(
            "diagram20.csv",
            Generator._run_query(
                """
                SELECT s.round,
                    max(t.finished) AS finished,
                    min(t.started) AS started,
                    max(finished) - min(started) AS duration
                FROM scalabilitytest s
                    LEFT OUTER JOIN tests t ON s.sid = t.sid
                GROUP BY s.round;
                """
            )
        )


def _generate_diagram_data(name: Optional[str] = None) -> None:
    if name:
        getattr(Generator, name)()
    else:
        for attr in dir(Generator):
            if attr.startswith("diagram_"):
                getattr(Generator, attr)()


if __name__ == "__main__":
    _generate_diagram_data()
