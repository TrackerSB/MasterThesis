-- FIXME Make sure only submissions of user "test" are considered

-----------------------
-- Utility functions --
-----------------------
CREATE OR REPLACE FUNCTION array_avg(DOUBLE PRECISION[])
    RETURNS DOUBLE PRECISION AS
$$
SELECT avg(v)
FROM unnest($1) g(v)
$$ LANGUAGE SQL;

----------------------
-- Scalability test --
----------------------
SELECT value, number
FROM (
         SELECT status AS value, count(*) AS number, 1 AS ranking
         FROM tests
         GROUP BY status
         UNION
         SELECT result, count(*), 2
         FROM tests
         GROUP BY result
         UNION
         SELECT 'total', count(*), 3
         FROM tests
     ) AS results
ORDER BY ranking ASC, number DESC;

--------------------
-- Challenge test --
--------------------

-- FIXME Is the average calculation for markings and numSegments correct? Does it change "weights"?
-- Test Generators
SELECT ctg.author,
       count(*)                        AS numTests,
       avg(ctg.finished - ctg.started) AS generationTime,
       avg(t.finished - t.started)     AS executionTime,
       failed,
       avg(cast(invalid AS INT))       AS invalid,
       avg(numlanes)                   AS numLanes,
       avg(avgNumSegments)             AS numSegments,
       avg(avgMarkings)                AS markings,
       avg(numParticipants)            AS numParticipants,
       avg(avgGoalArea)                AS goalArea,
       avg(avgInvalidGoalArea)         AS invalidGoalArea,
       avg(avgInitialCarToLaneAngle)   AS initialCarToLaneAngle
FROM (
         SELECT ctgi.*,
                array_avg(numsegments)            AS avgNumSegments,
                array_avg(markings)               AS avgMarkings,
                count(*)                          AS numParticipants,
                avg(goalarea)                     AS avgGoalArea,
                avg(cast(invalidgoalarea AS INT)) AS avgInvalidGoalArea,
                avg(initialcartolaneangle)        AS avgInitialCarToLaneAngle
         FROM challengetestgenerator ctgi
                  LEFT OUTER JOIN challengetestai cta ON ctgi.sid = cta.sid
         GROUP BY gid, goalarea
     ) ctg
         LEFT OUTER JOIN tests t ON ctg.sid = t.sid
GROUP BY ctg.author, failed
ORDER BY author;

SELECT author,
       avg(cta.finished - cta.started) AS drivingDuration,
       avg(cta.travelleddistance)      AS travelledDistance
FROM challengetestai cta
GROUP BY cta.author;

-----------------------
-- Simple statistics --
-----------------------
SELECT result, status, count(*)
FROM tests
GROUP BY result, status;
