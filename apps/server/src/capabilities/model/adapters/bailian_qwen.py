from collections.abc import AsyncIterator

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncOpenAI,
    AuthenticationError,
    PermissionDeniedError,
    RateLimitError,
)
from openai.types.chat import ChatCompletionMessageParam

from capabilities.model.gateway import (
    ModelGatewayAuthenticationError,
    ModelGatewayConfigurationError,
    ModelGatewayRateLimitError,
    ModelGatewayTimeoutError,
    ModelGatewayUnavailableError,
    ModelMessage,
    ModelRequest,
    ModelResponse,
)


class BailianQwenAdapter:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float = 60.0,
        max_tokens: int = 2048,
        client: AsyncOpenAI | None = None,
    ) -> None:
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        self._max_tokens = max_tokens
        self._client = client

    async def complete(self, request: ModelRequest) -> ModelResponse:
        if not self._api_key:
            raise ModelGatewayConfigurationError("未配置百炼 API Key")

        try:
            completion = await self._get_client().chat.completions.create(
                model=self._model,
                messages=[self._to_openai_message(message) for message in request.messages],
                max_tokens=self._max_tokens,
            )
        except (AuthenticationError, PermissionDeniedError) as error:
            raise ModelGatewayAuthenticationError("百炼 API Key 无效或没有模型权限") from error
        except RateLimitError as error:
            raise ModelGatewayRateLimitError("百炼请求过于频繁或额度不足") from error
        except APITimeoutError as error:
            raise ModelGatewayTimeoutError("百炼请求超时") from error
        except (APIConnectionError, APIStatusError) as error:
            raise ModelGatewayUnavailableError("百炼服务当前不可用") from error

        if not completion.choices:
            raise ModelGatewayUnavailableError("百炼返回了空响应")

        content = completion.choices[0].message.content
        if not content or not content.strip():
            raise ModelGatewayUnavailableError("百炼返回了空内容")

        return ModelResponse(content=content.strip())

    async def stream(self, request: ModelRequest) -> AsyncIterator[str]:
        if not self._api_key:
            raise ModelGatewayConfigurationError("未配置百炼 API Key")

        try:
            stream = await self._get_client().chat.completions.create(
                model=self._model,
                messages=[self._to_openai_message(message) for message in request.messages],
                max_tokens=self._max_tokens,
                stream=True,
            )
            async for chunk in stream:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except (AuthenticationError, PermissionDeniedError) as error:
            raise ModelGatewayAuthenticationError("百炼 API Key 无效或没有模型权限") from error
        except RateLimitError as error:
            raise ModelGatewayRateLimitError("百炼请求过于频繁或额度不足") from error
        except APITimeoutError as error:
            raise ModelGatewayTimeoutError("百炼请求超时") from error
        except (APIConnectionError, APIStatusError) as error:
            raise ModelGatewayUnavailableError("百炼服务当前不可用") from error

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=self._api_key,
                base_url=self._base_url,
                timeout=self._timeout_seconds,
                max_retries=1,
            )
        return self._client

    @staticmethod
    def _to_openai_message(message: ModelMessage) -> ChatCompletionMessageParam:
        if message.role == "assistant":
            return {"role": "assistant", "content": message.content}
        if message.role == "system":
            return {"role": "system", "content": message.content}
        return {"role": "user", "content": message.content}
