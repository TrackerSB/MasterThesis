from logging import getLogger
from os.path import join, dirname

from dataclasses import dataclass
from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from typing import List

TEMPLATE_PATH = join(dirname(__file__), "..", "templates")
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
DBE_TEMPLATE_NAME = "ai_stress_environment.dbe.xml"
DBC_TEMPLATE_NAME = "ai_stress_criteria.dbc.xml"
OUTPUT_DIRECTORY = Path(join(dirname(__file__), "..", "generated_ai_stress"))
MODES_TO_TEST = ["MANUAL", "TRAINING"]
# Denotes by which number the number of generated files has to be divisible
GENERATED_FILES_FACTOR = len(MODES_TO_TEST) + 1
_LOGGER = getLogger("SubmissionTester.TestTypes.AIScalabilityTest")


@dataclass
class AIScalabilityStat():
    sid: SimulationID = None
    mode: str = None
    num_participants: int = None


def ai_scalability_generation(max_num_participants: int, distance_between_lanes: float = 10, lane_width: float = 8,
                              length: float = 500, output_dir: Path = OUTPUT_DIRECTORY) -> List[Path]:
    from shutil import rmtree
    if lane_width > (distance_between_lanes + 1):
        raise ValueError("The distance is too small to fit in lanes with the given width and walls separating them.")
    rmtree(output_dir.as_posix(), ignore_errors=True)
    output_dir.mkdir(exist_ok=True, parents=True)
    generated_paths = []
    for num_participants in range(1, max_num_participants + 1):
        prefix = "ai_stress_" + str(num_participants) + "_participants"
        dbe_content = TEMPLATE_ENV.get_template(DBE_TEMPLATE_NAME) \
            .render(numParticipants=num_participants,
                    distanceBetweenLanes=distance_between_lanes,
                    laneWidth=lane_width,
                    length=length)
        dbe_file_path = output_dir.joinpath(prefix + ".dbe.xml")
        with dbe_file_path.open("w") as dbe_file:
            dbe_file.write(dbe_content)
        generated_paths.append(dbe_file_path)
        for movement_mode in MODES_TO_TEST:
            dbc_content_reference = TEMPLATE_ENV.get_template(DBC_TEMPLATE_NAME) \
                .render(testName="TestWith" + str(num_participants) + "ParticipantsInMode" + movement_mode,
                        dbeFileName=prefix + ".dbe.xml",
                        movementMode=movement_mode,
                        numParticipants=num_participants,
                        distanceBetweenLanes=distance_between_lanes,
                        laneWidth=lane_width,
                        length=length)
            dbc_file_path = output_dir.joinpath(prefix + "_" + movement_mode + ".dbc.xml")
            with dbc_file_path.open("w") as dbc_file:
                dbc_file.write(dbc_content_reference)
            generated_paths.append(dbc_file_path)
    return generated_paths


def _handle_ai_dummy(service: AIExchangeService, sid: SimulationID, vid: VehicleID) -> None:
    from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse
    while True:
        sim_state = service.wait_for_simulator_request(sid, vid)
        if sim_state is not SimStateResponse.SimState.RUNNING:
            break


def ai_scalability_execution(service: AIExchangeService, ai_scalability_paths: List[Path]) -> List[AIScalabilityStat]:
    from test_types import get_vids_by_path
    from threading import Thread
    from xml_util import parse_xml, find
    # NOTE Relies on same prefix for related DBCs and DBEs
    test_file_paths = sorted([p for p in OUTPUT_DIRECTORY.iterdir() if p.is_file()], key=lambda p: p.as_posix())
    if len(test_file_paths) % GENERATED_FILES_FACTOR != 0:
        raise ValueError("The number of test file paths has to be divisible by " + str(GENERATED_FILES_FACTOR) + ".")
    stats = []
    for i in range(0, len(ai_scalability_paths), GENERATED_FILES_FACTOR):
        dbe_file_path = ai_scalability_paths[i]
        for j in range(1, GENERATED_FILES_FACTOR):
            dbc_file_path = ai_scalability_paths[i + j]
            submissions = service.run_tests("test", "test", dbe_file_path, dbc_file_path)
            if submissions and submissions.submissions:
                assert len(submissions.submissions) == 1, "The submitted tests must contain exactly one SimulationID."
                for _, sid in submissions.submissions.items():
                    _, vids = get_vids_by_path(dbc_file_path)
                    scalability_stat = AIScalabilityStat()
                    scalability_stat.sid = sid
                    scalability_stat.mode = find(parse_xml(dbc_file_path), "//db:initialState").get("movementMode")
                    scalability_stat.num_participants = len(vids)
                    _LOGGER.info("Run AI scalability test with " + str(scalability_stat.num_participants)
                                 + " participants in mode " + scalability_stat.mode)
                    ai_threads = []
                    for vid in vids:
                        thread = Thread(target=_handle_ai_dummy, args=(service, sid, vid))
                        thread.start()
                        ai_threads.append(thread)
                    for thread in ai_threads:
                        thread.join()
                    stats.append(scalability_stat)
            else:
                _LOGGER.error("The generated AI scalability tests were not accepted by DriveBuild.")
    return stats
