from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal, Protocol

ModelRole = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class ModelMessage:
    role: ModelRole
    content: str


@dataclass(frozen=True, slots=True)
class ModelRequest:
    messages: tuple[ModelMessage, ...]


@dataclass(frozen=True, slots=True)
class ModelResponse:
    content: str


class ModelGateway(Protocol):
    async def complete(self, request: ModelRequest) -> ModelResponse:
        ...

    def stream(self, request: ModelRequest) -> AsyncIterator[str]:
        ...


class ModelGatewayError(RuntimeError):
    """Base error raised by a model provider adapter."""


class ModelGatewayConfigurationError(ModelGatewayError):
    pass


class ModelGatewayAuthenticationError(ModelGatewayError):
    pass


class ModelGatewayRateLimitError(ModelGatewayError):
    pass


class ModelGatewayTimeoutError(ModelGatewayError):
    pass


class ModelGatewayUnavailableError(ModelGatewayError):
    pass
