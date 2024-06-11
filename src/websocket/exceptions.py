class Error(Exception):
    code: int
    message: str

    def __init__(self, message=None):
        if message:
            self.message = message

    @property
    def error(self):
        return f"Error code: {self.code}, message: {self.message}"


# Server exceptions
class ServerError(Error):
    code = 1


class UnknownType(Error):
    code = 2
    message = "Unknown data type, allowed types: init, success_auth, data, error"


# Client exceptions
class WebSocketNotConnectedError(Error):
    code = 3
    message = "Connect to the websocket first"
