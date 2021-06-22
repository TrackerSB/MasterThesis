import time

from typing import Callable

from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID
from lxml.etree import _Element, Element

from DDController import Controller

ACC_GAIN: float = 0.5
BRAKE_GAIN: float = 1.0
BRIGHTNESS: float = 0.4
MAX_SPEED: float = 25


class AI:
    def __init__(self, service: AIExchangeService):
        self.service = service

    # The Image needs to be preprocessed
    @staticmethod
    def _preprocess(img, brightness):
        from cv2 import cvtColor, resize, COLOR_HSV2BGR, COLOR_BGR2HSV
        from numpy import array
        pil_image = img.convert('RGB')
        open_cv_image = array(pil_image)
        open_cv_image = open_cv_image[:, :, ::-1].copy()
        hsv = cvtColor(resize(open_cv_image, (280, 210)), COLOR_BGR2HSV)
        hsv[..., 2] = hsv[..., 2] * brightness
        preprocessed = cvtColor(hsv, COLOR_HSV2BGR)
        return preprocessed

    def _translate_steering(original_steering_value):
        # Using a quadratic function might be too much
        # newValue = -1.0 * (0.4 * pow(original_steering_value, 2) + 0.6 * original_steering_value + 0)
        # This seems to over shoot. Maybe it's just a matter of speed and not amount of steering
        newValue = -1.0 * original_steering_value
        linear_factor = 0.6
        # Dump the controller to compensate oscillations in gentle curve
        if abs(original_steering_value) < 1:
            newValue = linear_factor * newValue

        # print("Steering", original_steering_value, " -> ", newValue)
        return newValue

    def start(self, sid: SimulationID, vid: VehicleID, dynamic_stats_callback: Callable[[], None]) -> None:
        from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse, DataRequest, Control
        from PIL import Image
        from io import BytesIO
        import speed_dreams as sd
        # Setup the SHM with DeepDrive
        # Create shared memory object
        Memory = sd.CSharedMemory(TargetResolution=[280, 210])
        # Enable Pause-Mode
        Memory.setSyncMode(True)

        Memory.Data.Game.UniqueRaceID = int(time.time())
        print("Setting Race ID at ", Memory.Data.Game.UniqueRaceID)

        # Setting Max_Speed for the Vehicle.
        # TODO What's this? Maybe some hacky way to pass a parameter which is not supposed to be there...

        Memory.Data.Game.UniqueTrackID = int(MAX_SPEED)
        # Speed is KM/H
        print("Setting speed at ", Memory.Data.Game.UniqueTrackID)
        # Default for AsFault
        Memory.Data.Game.Lanes = 1
        # By default the AI is in charge
        Memory.Data.Control.IsControlling = 1
        Memory.waitOnRead()
        if Memory.Data.Control.Breaking == 3.0 or Memory.Data.Control.Breaking == 2.0:
            print("\n\n\nState not reset ! ", Memory.Data.Control.Breaking)
            Memory.Data.Control.Breaking = 0.0
            # Pass the computation to DeepDrive
            # Not sure this will have any effect
            Memory.indicateWrite()

        Memory.waitOnRead()
        if Memory.Data.Control.Breaking == 3.0 or Memory.Data.Control.Breaking == 2.0:
            print("\n\n\nState not reset Again! ", Memory.Data.Control.Breaking)
            Memory.Data.Control.Breaking = 0.0
            # Pass the computation to DeepDrive
            Memory.indicateWrite()
        while True:
            sim_state = self.service.wait_for_simulator_request(sid, vid)
            if sim_state == SimStateResponse.SimState.RUNNING:
                dynamic_stats_callback()
                request = DataRequest()
                request.request_ids.append("egoFrontCamera_" + vid.vid)
                data = self.service.request_data(sid, vid, request)
                if data:
                    speed = data.data["egoSpeed_" + vid.vid].speed.speed
                    color_image = Image.open(BytesIO(data.data["egoFrontCamera_" + vid.vid].camera.color))
                    imageData = AI._preprocess(color_image, BRIGHTNESS)
                    Height, Width = imageData.shape[:2]
                    # print("Image size ", Width, Height)
                    # TODO Size of image should be right since the beginning
                    Memory.write(Width, Height, imageData, speed)

                    # Pass the computation to DeepDrive
                    Memory.indicateWrite()

                    # Wait for the control commands to send to the vehicle
                    # This includes a sleep and will be unlocked by writing data to it
                    Memory.waitOnRead()
                    steering = round(AI._translate_steering(Memory.Data.Control.Steering), 3)
                    throttle = round(Memory.Data.Control.Accelerating * ACC_GAIN, 3)
                    brake = round(Memory.Data.Control.Breaking * BRAKE_GAIN, 3)
                    
                    
                    control = Control()
                    control.avCommand.steer = steering
                    control.avCommand.accelerate = throttle
                    control.avCommand.brake = brake
                    self.service.control(sid, vid, control)
                else:
                    print("The request for data returned None.")
            else:
                break


    @staticmethod
    def add_data_requests(parent: _Element, participant: str) -> None:
        speed_node = Element("speed")
        speed_node.set("id", "egoSpeed_" + participant)
        parent.append(speed_node)
        camera_node = Element("camera")
        camera_node.set("id", "egoFrontCamera_" + participant)
        camera_node.set("width", "280")
        camera_node.set("height", "210")
        camera_node.set("direction", "FRONT")
        camera_node.set("fov", "50")
        parent.append(camera_node)
