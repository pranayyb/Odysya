from utils.logger import get_logger

_error_logger = get_logger("ErrorHandler")


class Error(Exception):
    def __init__(self, message: str, code: int = 500):
        super().__init__(message)
        self.code = code
        _error_logger.error(f"[{self.__class__.__name__}] (code={code}) {message}")


class AgentError(Error):
    def __init__(self, message: str, agent_name: str = "unknown", code: int = 500):
        self.agent_name = agent_name
        super().__init__(f"AgentError({agent_name}): {message}", code)


class ToolError(Error):
    def __init__(self, message: str, tool_name: str = "unknown", code: int = 500):
        self.tool_name = tool_name
        super().__init__(f"ToolError({tool_name}): {message}", code)


class ClientError(Error):
    def __init__(self, message: str, client_name: str = "unknown", code: int = 500):
        self.client_name = client_name
        super().__init__(f"ClientError({client_name}): {message}", code)


class ServerError(Error):
    def __init__(self, message: str, server_name: str = "unknown", code: int = 500):
        self.server_name = server_name
        super().__init__(f"ServerError({server_name}): {message}", code)


def handle_error(e: Exception) -> dict:
    return {
        "error": str(e),
        "code": getattr(e, "code", 500),
        "type": e.__class__.__name__,
    }
