input metauml;

% Default values
linkDist := 40;
offset := 15;

% Simple messages
beginfig(1);
    Class.DataRequest("DataRequest")
        ("+request_ids: repeated string")
        ();

    Class.VehicleID("VehicleID")
        ("+vid: string")
        ();

    Class.VehicleIDs("VehicleIDs")
        ("+vids: repeated string")
        ();

    Class.VerificationResult("VerificationResult")
        ("+precondition: string",
            "+failure: string",
            "+success: string")
        ();

    Class.SimulationIDs("SimulationIDs")
        ("+sids: repeated string")
        ();

    Class.Num("Num")
        ("+num: int")
        ();

    Class.Bool("Bool")
        ("+value: bool")
        ();

    Class.User("User")
        ("+username: string",
            "+password: string")
        ();

    topToBottom(offset)(VehicleID, VehicleIDs, Bool);
    topToBottom(offset)(DataRequest, VerificationResult, SimulationIDs);
    DataRequest.w = VehicleID.e + (20, 0);
    topToBottom(offset)(Num, User);
    Num.w = DataRequest.e + (20, 0);
    drawObjects(VehicleID, VehicleIDs, DataRequest, VerificationResult, SimulationIDs, Num, User, Bool);
endfig;

% Complex messages
beginfig(2);
    % Data and DataResponse
    Class.DataResponse("DataResponse")
        ("+data: map<string, Data>")
        ();

    Class.Data("Data")
        ("-data: oneof")
        ();

    Class.OneOfData("oneof")
        ("+position: Position",
            "+speed: Speed",
            "+angle: SteeringAngle",
            "+lidar: Lidar",
            "+camera: Camera",
            "+damage: Damage",
            "+lane_center_distance: LaneCenterDistance",
            "+car_to_lane_angle: CarToLaneAngle",
            "+error: Error"
        )
        ();
    Class_stereotypes.OneOfData("<<abstract>>");

    Class.Position("Position")
        ("+x: double",
            "+y: double")
        ();

    Class.Speed("Speed")
        ("+speed: double")
        ();

    Class.SteeringAngle("SteeringAngle")
        ("+angle: double")
        ();

    Class.Lidar("Lidar")
        ("+points: repeated double")
        ();

    Class.Camera("Camera")
        ("+color: bytes",
            "+annotated: bytes",
            "+depth: bytes")
        ();

    Class.Damage("Damage")
        ("+is_damaged: bool")
        ();

    Class.LaneCenterDistance("LaneCenterDistance")
        ("+lane_id: string",
            "+distance: float")
        ();

    Class.CarToLaneAngle("CarToLaneAngle")
        ("+lane_id: string",
            "+angle: float")
        ();

    Class.BoundingBox("BoundingBox")
        ("+points: repeated float")
        ();

    Class.Error("Error")
        ("+message: string")
        ();

    topToBottom(linkDist)(DataResponse, Data, OneOfData);
    topToBottom.left(offset)(Position, Speed, SteeringAngle, Lidar, Camera, Damage, LaneCenterDistance, CarToLaneAngle, BoundingBox, Error);
    Camera.w = OneOfData.e + (linkDist, 0);
    drawObjects(DataResponse, Data, OneOfData,Position, Speed, SteeringAngle, Lidar, Camera, Damage, LaneCenterDistance, CarToLaneAngle, BoundingBox, Error);

    link(dependency)(rpathVertical(Data.n, DataResponse.bottom));
    link(dependency)(rpathVertical(OneOfData.n, Data.bottom));
    pair preCamera;
    preCamera = Camera.w - (offset, 0);
    path position;
    position = Position.w -- Position.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(position);
    path speed;
    speed = Speed.w -- Speed.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(speed);
    path steeringAngle;
    steeringAngle = SteeringAngle.w -- SteeringAngle.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(steeringAngle);
    path lidar;
    lidar = Lidar.w -- Lidar.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(lidar);
    path camera;
    camera = Camera.w -- Camera.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(camera);
    path damage;
    damage = Damage.w -- Damage.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(damage);
    path laneCenterDistance;
    laneCenterDistance = LaneCenterDistance.w -- LaneCenterDistance.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(laneCenterDistance);
    path carToLaneAngle;
    carToLaneAngle = CarToLaneAngle.w -- CarToLaneAngle.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(carToLaneAngle);
    path boundingBox;
    boundingBox = BoundingBox.w -- BoundingBox.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(boundingBox);
    path error;
    error = Error.w -- Error.w - (offset, 0) -- preCamera -- OneOfData.e;
    link(inheritance)(error);

    % Control
    Class.Control("Control")
        ("-command: oneof")
        ();

    Class.OneOfControl("oneof")
        ("+avCommand: AvCommand",
            "+simCommand: SimCommand")
        ();
    Class_stereotypes.OneOfControl("<<abstract>>");

    Class.AvCommand("AvCommand")
        ("+accelerate: double",
            "+steer: double",
            "+brake: double")
        ();

    Class.SimCommand("SimCommand")
        ("+command: Command")
        ();

    Class.Command("Command")
        ("SUCCEED",
            "FAIL",
            "CANCEL")
        ();
    Class_stereotypes.Command("<<enum>>");
    Class_noVisibilityMarkers.Command;

    topToBottom.left(linkDist)(Control, OneOfControl, AvCommand);
    topToBottom.right(linkDist)(Command, SimCommand);
    pair preAvCommand;
    preAvCommand := AvCommand.n + (0, offset);
    SimCommand.nw = AvCommand.ne + (offset, 0);
    pair preSimCommand;
    preSimCommand := SimCommand.n + (0, offset);
    SimCommand.ne = OneOfData.s + (20, -110); % Position this sub-figure
    drawObjects(Control, OneOfControl, AvCommand, SimCommand, Command);

    link(dependency)(pathVertical(Control.s, OneOfControl.top));
    link(inheritance)(pathVertical(AvCommand.n, OneOfControl.bottom));
    path simCommand;
    simCommand = SimCommand.n -- preSimCommand -- pathVertical(preAvCommand, OneOfControl.bottom);
    link(inheritance)(simCommand);
    link(dependency)(rpathVertical(Command.s, SimCommand.top));

    % TestResult
    Class.TestResult("TestResult")
        ("+result: Result")
        ();

    Class.Result("Result")
        ("SUCCEEDED",
            "FAILED",
            "SKIPPED",
            "UNKNOWN")
        ();
    Class_stereotypes.Result("<<enum>>");
    Class_noVisibilityMarkers.Result;

    topToBottom(linkDist)(TestResult, Result);
    Result.s = Control.n + (0, offset); % Position this sub-figure
    drawObjects(TestResult, Result);

    clink(dependency)(TestResult, Result);

    % SimStateResponse
    Class.SimStateResponse("SimStateResponse")
        ("+state: SimState")
        ();

    Class.SimState("SimState")
        ("RUNNING",
            "FINISHED",
            "CANCELED",
            "TIMEOUT",
            "UNKNOWN")
        ();
    Class_stereotypes.SimState("<<enum>>");
    Class_noVisibilityMarkers.SimState;

    topToBottom(linkDist)(SimStateResponse, SimState);
    SimState.s = TestResult.n + (0, offset); % Position this sub-figure
    drawObjects(SimStateResponse, SimState);

    clink(dependency)(SimStateResponse, SimState);

    % SubmissionResult
    Class.SubmissionResult("SubmissionResult")
        ("-may_submissions: oneof")
        ();

    Class.OneOfSubmissionResult("oneof")
        ("+message: Void",
            "+result: Submissions")
        ();
    Class_stereotypes.OneOfSubmissionResult("<<abstract>>");

    Class.Void("Void")
        ("+message: string")
        ();

    Class.Submissions("Submissions")
        ("+submissions: map<string, SimulationID>")
        ();

    Class.SimulationID("SimulationID")
        ("+sid: string")
        ();

    topToBottom(linkDist)(OneOfSubmissionResult, SubmissionResult);
    topToBottom.left(offset)(Submissions, Void);
    Submissions.w = OneOfSubmissionResult.e + (linkDist, 0);
    SimulationID.w = Void.se + (offset, 0);
    SubmissionResult.sw = DataResponse.nw + (-25, offset); % Position this sub-figure
    drawObjects(SubmissionResult, OneOfSubmissionResult, Submissions, SimulationID, Void);

    clink(dependency)(SubmissionResult, OneOfSubmissionResult);
    clink(inheritance)(Submissions, OneOfSubmissionResult);
    pair preSubmissions;
    preSubmissions = Submissions.w - (offset, 0);
    pair preVoid;
    preVoid = Void.w - (offset, 0);
    path void;
    void = Void.w -- preVoid -- preSubmissions -- OneOfSubmissionResult.e;
    link(inheritance)(void);
    link(dependency)(pathVertical(SimulationID.n, Submissions.bottom));
endfig;
end
