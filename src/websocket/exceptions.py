class Error(Exception):
    code: int
    message: str

    def __init__(self, message=None):
        if message:
            self.message = message

    @property
    def error(self):
        return f"Error code: {self.code}, message: {self.message}"


class WebSocketNotConnectedError(Error):
    code = 3
    message = "Connect to the websocket first"


class InvalidTokenException(Error):
    code = 1
    message = "Invalid token"


class ExpiredTokenException(Error):
    code = 2
    message = "Expired token"


class UnexpectedTokenException(Error):
    code = 3
    message = "Unknown token error"
