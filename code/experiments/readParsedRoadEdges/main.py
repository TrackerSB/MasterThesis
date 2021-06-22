from os.path import dirname, join

_input_path = join(dirname(__file__), "input")
_file_names = [
    "roadEdges_1.txt",
    "roadEdges_2.txt",
    "roadEdges_3.txt"
]


def _main() -> None:
    from drivebuildclient.aiExchangeMessages_pb2 import DataResponse
    for file_name in _file_names:
        file_path = join(_input_path, file_name)
        with open(file_path, "rb") as file:
            data = DataResponse()
            serialized_data = file.read()
            data.ParseFromString(serialized_data)
            print(str(data))


if __name__ == "__main__":
    _main()
