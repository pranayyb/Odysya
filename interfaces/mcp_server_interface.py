from abc import ABC, abstractmethod
from typing import Any, Dict


class MCPServer(ABC):
    """
    unified interface for all mcp servers.
    """

    @abstractmethod
    async def register_tools(self) -> None:
        """
        register tools for the MCP Server
        """
        pass

    @abstractmethod
    async def handle_request(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """
        handling request from the mcp client
        """
        pass

    @abstractmethod
    def toggle_mock_mode(self, enable_mock: bool) -> str:
        """
        switching b/w mock and actual apis
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        starting the server!!!!!!!!
        """
        pass
