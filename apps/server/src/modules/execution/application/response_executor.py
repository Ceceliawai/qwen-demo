from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class ExecutionRequest:
    conversation_id: UUID
    user_content: str
    history: tuple[dict[str, str], ...]


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    content: str


class ResponseExecutor(Protocol):
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        ...


class FakeResponseExecutor:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(content=f"收到你的消息：{request.user_content}")
