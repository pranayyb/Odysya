from abc import ABC, abstractmethod


class AgentToolInterface(ABC):
    @abstractmethod
    async def run(self, query: str) -> str:
        pass
