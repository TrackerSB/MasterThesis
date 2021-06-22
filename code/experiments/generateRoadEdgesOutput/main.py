from logging import getLogger

from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import VehicleID, DataRequest, TestResult, DataResponse
from lxml.etree import _ElementTree, XMLParser
from pathlib import Path
from typing import Optional

_service = AIExchangeService("defender.fim.uni-passau.de", 8383)
_vid = VehicleID()
_vid.vid = "ego"
_request = DataRequest()
_request.request_ids.extend(["egoRoadEdges", "visualizer_ego_boundingBox"])
_result = TestResult()
_result.result = TestResult.Result.SKIPPED
_logger = getLogger("GenerateRoadEdgesOutput.Main")
_SCHEMALESS_PARSER = XMLParser(recover=False, remove_comments=True)
_NAMESPACES = {
    "db": "http://drivebuild.com"
}


def _parse_xml(path: Path) -> Optional[_ElementTree]:
    from lxml.etree import parse
    try:
        tree = parse(path.as_posix(), _SCHEMALESS_PARSER)  # May throw XMLSyntaxException
    except Exception as ex:
        _logger.warning("Parsing of \"" + path.as_posix() + "\" failed due to " + str(ex))
        tree = None
    return tree


def _prepare_test(dbe_path: Path, dbc_path: Path) -> None:
    from lxml.etree import Element, tostring
    dbc_tree = _parse_xml(dbc_path)
    ego_vehicle_node = dbc_tree.find("//db:participant[@id='ego']", namespaces=_NAMESPACES)
    ai_node = ego_vehicle_node.find("db:ai", namespaces=_NAMESPACES)
    if not ai_node:
        ai_node = Element("ai")
        ego_vehicle_node.append(ai_node)
    road_edges_node = Element("roadEdges")
    road_edges_node.set("id", "egoRoadEdges")
    ai_node.append(road_edges_node)
    with open(dbc_path.as_posix(), "wb") as dbc_file:
        dbc_file.write(tostring(dbc_tree))


def _main() -> None:
    from reference.generator import ReferenceTestGenerator
    from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse
    test = ReferenceTestGenerator.generate_random_test()
    if test:
        _prepare_test(test[0], test[2])
        submission_result = _service.run_tests("test", "test", test[0], test[2])
        if submission_result and submission_result.submissions:
            for _, sid in submission_result.submissions.items():
                try:
                    counter = 0
                    while True:
                        sim_state = _service.wait_for_simulator_request(sid, _vid)
                        if sim_state == SimStateResponse.RUNNING:
                            data = _service.request_data(sid, _vid, _request)
                            serialized = data.SerializeToString()
                            with open("dataResponse_" + str(counter) + ".txt", "wb") as out_file:
                                out_file.write(serialized)
                            counter = counter + 1
                        else:
                            break
                finally:
                    _service.control_sim(sid, _result)


if __name__ == "__main__":
    _main()
