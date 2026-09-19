from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from capabilities.model.gateway import (
    ModelGateway,
    ModelGatewayAuthenticationError,
    ModelGatewayConfigurationError,
    ModelGatewayRateLimitError,
    ModelGatewayTimeoutError,
    ModelGatewayUnavailableError,
    ModelMessage,
    ModelRequest,
)
from modules.execution.application.errors import (
    ResponseAuthenticationError,
    ResponseConfigurationError,
    ResponseRateLimitError,
    ResponseTimeoutError,
    ResponseUnavailableError,
)

SYSTEM_PROMPT = (
    "你是 Qwen Workspace 中的 AI 助手。请准确、清晰地回答用户问题；"
    "遇到不确定的信息时明确说明。"
)


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

    def stream(self, request: ExecutionRequest) -> AsyncIterator[str]:
        ...


class ModelResponseExecutor:
    def __init__(self, gateway: ModelGateway) -> None:
        self._gateway = gateway

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        model_request = self._build_model_request(request)

        try:
            response = await self._gateway.complete(model_request)
        except ModelGatewayConfigurationError as error:
            raise ResponseConfigurationError(str(error)) from error
        except ModelGatewayAuthenticationError as error:
            raise ResponseAuthenticationError(str(error)) from error
        except ModelGatewayRateLimitError as error:
            raise ResponseRateLimitError(str(error)) from error
        except ModelGatewayTimeoutError as error:
            raise ResponseTimeoutError(str(error)) from error
        except ModelGatewayUnavailableError as error:
            raise ResponseUnavailableError(str(error)) from error

        return ExecutionResult(content=response.content)

    async def stream(self, request: ExecutionRequest) -> AsyncIterator[str]:
        received_content = False
        try:
            async for content in self._gateway.stream(self._build_model_request(request)):
                received_content = True
                yield content
        except ModelGatewayConfigurationError as error:
            raise ResponseConfigurationError(str(error)) from error
        except ModelGatewayAuthenticationError as error:
            raise ResponseAuthenticationError(str(error)) from error
        except ModelGatewayRateLimitError as error:
            raise ResponseRateLimitError(str(error)) from error
        except ModelGatewayTimeoutError as error:
            raise ResponseTimeoutError(str(error)) from error
        except ModelGatewayUnavailableError as error:
            raise ResponseUnavailableError(str(error)) from error

        if not received_content:
            raise ResponseUnavailableError("百炼返回了空内容")

    @staticmethod
    def _build_model_request(request: ExecutionRequest) -> ModelRequest:
        messages = [ModelMessage(role="system", content=SYSTEM_PROMPT)]
        for message in request.history:
            role = message["role"]
            if role == "system":
                messages.append(ModelMessage(role="system", content=message["content"]))
            elif role == "assistant":
                messages.append(ModelMessage(role="assistant", content=message["content"]))
            elif role == "user":
                messages.append(ModelMessage(role="user", content=message["content"]))
        messages.append(ModelMessage(role="user", content=request.user_content))
        return ModelRequest(messages=tuple(messages))


class FakeResponseExecutor:
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        return ExecutionResult(content=f"收到你的消息：{request.user_content}")

    async def stream(self, request: ExecutionRequest) -> AsyncIterator[str]:
        yield f"收到你的消息：{request.user_content}"
