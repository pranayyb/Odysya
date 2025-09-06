class Error(Exception):
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.code = code


class AgentError(Error):
    def __init__(self, message: str, code: int = 500):
        super().__init__(f"AgentError: {message}", code)


class ToolError(Error):
    def __init__(self, message: str, code: int = 500):
        super().__init__(f"ToolError: {message}", code)


class ClientError(Error):
    def __init__(self, message: str, code: int = 500):
        super().__init__(f"ClientError: {message}", code)


class ServerError(Error):
    def __init__(self, message: str, code: int = 500):
        super().__init__(f"ServerError: {message}", code)


def handle_error(e: Exception):
    return {
        "error": str(e),
        "code": getattr(e, "code", 500),
        "type": e.__class__.__name__,
    }
