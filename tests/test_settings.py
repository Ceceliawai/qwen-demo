from bootstrap.config.settings import Settings


def test_settings_have_safe_development_defaults() -> None:
    settings = Settings.model_construct()

    assert settings.app_env == "development"
    assert settings.bailian_api_key == ""
    assert settings.bailian_chat_model == "qwen-plus"
    assert settings.bailian_request_timeout_seconds == 60.0
    assert settings.bailian_max_tokens == 2048
