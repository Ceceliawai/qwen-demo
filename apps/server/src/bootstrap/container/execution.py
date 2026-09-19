from functools import lru_cache

from bootstrap.config.settings import get_settings
from capabilities.model.adapters.bailian_qwen import BailianQwenAdapter
from modules.execution.application.response_executor import (
    ModelResponseExecutor,
    ResponseExecutor,
)


@lru_cache
def get_response_executor() -> ResponseExecutor:
    settings = get_settings()
    gateway = BailianQwenAdapter(
        api_key=settings.bailian_api_key,
        base_url=settings.bailian_base_url,
        model=settings.bailian_chat_model,
        timeout_seconds=settings.bailian_request_timeout_seconds,
        max_tokens=settings.bailian_max_tokens,
    )
    return ModelResponseExecutor(gateway)
