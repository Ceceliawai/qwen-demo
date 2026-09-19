from collections.abc import AsyncIterator
from uuid import uuid4

from capabilities.model.gateway import ModelRequest, ModelResponse
from modules.execution.application.response_executor import (
    ExecutionRequest,
    ModelResponseExecutor,
)


class StubModelGateway:
    def __init__(self) -> None:
        self.request: ModelRequest | None = None

    async def complete(self, request: ModelRequest) -> ModelResponse:
        self.request = request
        return ModelResponse(content="模型回答")

    async def stream(self, request: ModelRequest) -> AsyncIterator[str]:
        self.request = request
        yield "流式"
        yield "回答"


async def test_model_response_executor_sends_history_and_current_message() -> None:
    gateway = StubModelGateway()
    executor = ModelResponseExecutor(gateway)

    result = await executor.execute(
        ExecutionRequest(
            conversation_id=uuid4(),
            user_content="继续解释",
            history=(
                {"role": "user", "content": "什么是 RAG？"},
                {"role": "assistant", "content": "RAG 是检索增强生成。"},
            ),
        )
    )

    assert result.content == "模型回答"
    assert gateway.request is not None
    assert [(message.role, message.content) for message in gateway.request.messages[1:]] == [
        ("user", "什么是 RAG？"),
        ("assistant", "RAG 是检索增强生成。"),
        ("user", "继续解释"),
    ]


async def test_model_response_executor_streams_gateway_chunks() -> None:
    gateway = StubModelGateway()
    executor = ModelResponseExecutor(gateway)

    chunks = [
        chunk
        async for chunk in executor.stream(
            ExecutionRequest(
                conversation_id=uuid4(),
                user_content="你好",
                history=(),
            )
        )
    ]

    assert chunks == ["流式", "回答"]
