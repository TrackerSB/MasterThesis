# Given an object submission_result of type SubmissionResult
# Given a declared test with name "<testA>"
print(submission_result.message.message)
print(submission_result.result.submissions["<testA>"].sid)

# Given an object data of type DataResponse
# Given declared request data with IDs "<requestA>" (RoadCenterDistance) and "<requestB>" (Speed) and an undeclared ID "<requestC>" (Error)
print(data.data["<requestA>"].road_center_distance.road_id)
print(data.data["<requestA>"].road_center_distance.distance)
print(data.data["<requestB>"].speed.speed)
print(data.data["<requestC>"].error.message)
