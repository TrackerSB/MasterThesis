if __name__ == "__main__":
    from aiExchangeMessages_pb2 import Control
    from urllib.parse import unquote
    get_param = "%0A%13%0A%0A%0A%08fancySid%12%05%0A%03ego%12%09%09%00%00%00%00%00%00%F0%3F"

    unquoted = unquote(get_param, encoding="hex")

    replaced = ""
    for idx, c in enumerate(get_param):
        if c == "%":
            hex_str = get_param[idx + 1: idx + 3]
            bytes_str = bytes.fromhex(hex_str).decode()
            replaced = replaced + bytes_str
        else:
            replaced = replaced + c

    control = Control()
    # control.ParseFromString(<?>)
