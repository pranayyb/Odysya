from abc import ABC, abstractmethod
from typing import Any, Dict


class MCPServer(ABC):
    """
    Abstract base class for all MCP servers.

    Every MCP server (Hotel, Restaurant, Weather, Transport, Events)
    must implement this interface to ensure consistent behavior.
    """

    @abstractmethod
    async def register_tools(self) -> None:
        """
        Register all tools exposed by this server.
        Tools should be decorated MCP functions that clients can call.
        """
        pass

    @abstractmethod
    async def handle_request(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        Handle a tool request from an MCP client.
        Dispatch to the registered tool function with given parameters.

        :param tool_name: Name of the tool to invoke
        :param params: Arguments for the tool
        :return: Tool result (can be dict, str, etc.)
        """
        pass

    @abstractmethod
    def toggle_mock_mode(self, enable_mock: bool) -> str:
        """
        Switch between mock and real API mode.

        :param enable_mock: True = mock data mode, False = live API mode
        :return: Confirmation string
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        Start the MCP server using stdio transport.

        This should set up the MCP FastMCP instance,
        register all tools, and then run the server.
        """
        pass
