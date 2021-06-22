CREATE TABLE IF NOT EXISTS GeneratorStressTest
(
    gid        SERIAL    NOT NULL PRIMARY KEY,
    started    TIMESTAMP NOT NULL,
    finished   TIMESTAMP NOT NULL,
    numTests   INT       NOT NULL,
    validTests INT[],
    -- Not supported yet according to https://commitfest.postgresql.org/17/1252/
    -- FOREIGN KEY (EACH ELEMENT OF validTests) REFERENCES tests (sid)
    author     TEXT      NOT NULL
);

CREATE TABLE IF NOT EXISTS ChallengeTestGenerator
(
    gid         SERIAL    NOT NULL PRIMARY KEY,
    sid         INT REFERENCES tests (sid),
    started     TIMESTAMP NOT NULL,
    finished    TIMESTAMP NOT NULL,
    rejected    BOOLEAN   NOT NULL,
    failed      BOOLEAN   NOT NULL,
    invalid     BOOLEAN   NOT NULL,
    numLanes    INT,
    numSegments INT[],
    markings    SMALLINT[],
    author      TEXT      NOT NULL,
    round       INT       NOT NULL,
    CHECK ( failed OR rejected OR invalid OR (numLanes NOTNULL AND numSegments NOTNULL AND markings NOTNULL))
);

CREATE TABLE IF NOT EXISTS ChallengeTestAI
(
    sid                   INT              NOT NULL REFERENCES tests (sid),
    vid                   TEXT             NOT NULL,
    started               TIMESTAMP        NOT NULL,
    finished              TIMESTAMP,
    timeout               BOOLEAN          NOT NULL,
    errored               BOOLEAN          NOT NULL,
    notMoving             BOOLEAN          NOT NULL,
    initialCarToLaneAngle DOUBLE PRECISION,
    goalArea              DOUBLE PRECISION NOT NULL,
    invalidGoalArea       BOOLEAN          NOT NULL,
    travelledDistance     DOUBLE PRECISION NOT NULL,
    author                TEXT             NOT NULL,
    PRIMARY KEY (sid, vid)
);

CREATE TABLE IF NOT EXISTS AIScalabilityTest
(
    sid             INT  NOT NULL REFERENCES tests (sid) PRIMARY KEY,
    numParticipants INT  NOT NULL,
    mode            TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ScalabilityTest
(
    sid      INT NOT NULL REFERENCES Tests (sid) PRIMARY KEY,
    round    INT NOT NULL,
    numNodes INT NOT NULL
);
