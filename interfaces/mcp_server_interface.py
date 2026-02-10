from abc import ABC, abstractmethod


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
    def start(self) -> None:
        """
        starting the server!!!!!!!!
        """
        pass
