from types import SimpleNamespace
from typing import cast
from unittest.mock import AsyncMock

import pytest
from openai import AsyncOpenAI

from capabilities.model.adapters.bailian_qwen import BailianQwenAdapter
from capabilities.model.gateway import (
    ModelGatewayConfigurationError,
    ModelMessage,
    ModelRequest,
)


async def test_bailian_adapter_calls_openai_compatible_chat_api() -> None:
    create = AsyncMock(
        return_value=SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=" 真实回复 "))]
        )
    )
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    adapter = BailianQwenAdapter(
        api_key="sk-test",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus",
        max_tokens=512,
        client=cast(AsyncOpenAI, client),
    )

    response = await adapter.complete(
        ModelRequest(
            messages=(
                ModelMessage(role="system", content="系统提示"),
                ModelMessage(role="user", content="你好"),
            )
        )
    )

    assert response.content == "真实回复"
    create.assert_awaited_once_with(
        model="qwen-plus",
        messages=[
            {"role": "system", "content": "系统提示"},
            {"role": "user", "content": "你好"},
        ],
        max_tokens=512,
    )


async def test_bailian_adapter_rejects_missing_api_key() -> None:
    adapter = BailianQwenAdapter(
        api_key="",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus",
    )

    with pytest.raises(ModelGatewayConfigurationError, match="API Key"):
        await adapter.complete(
            ModelRequest(messages=(ModelMessage(role="user", content="你好"),))
        )


async def test_bailian_adapter_streams_openai_compatible_chunks() -> None:
    async def chunks():
        yield SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content="你"))]
        )
        yield SimpleNamespace(
            choices=[SimpleNamespace(delta=SimpleNamespace(content="好"))]
        )

    create = AsyncMock(return_value=chunks())
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    adapter = BailianQwenAdapter(
        api_key="sk-test",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus",
        max_tokens=512,
        client=cast(AsyncOpenAI, client),
    )

    result = [
        content
        async for content in adapter.stream(
            ModelRequest(messages=(ModelMessage(role="user", content="你好"),))
        )
    ]

    assert result == ["你", "好"]
    create.assert_awaited_once_with(
        model="qwen-plus",
        messages=[{"role": "user", "content": "你好"}],
        max_tokens=512,
        stream=True,
    )
