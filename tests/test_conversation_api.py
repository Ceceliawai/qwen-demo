from httpx import ASGITransport, AsyncClient

from bootstrap.container.execution import get_response_executor
from bootstrap.database.init import create_tables
from bootstrap.database.session import engine
from main import app
from modules.execution.application.response_executor import FakeResponseExecutor


async def test_create_and_send_message() -> None:
    await create_tables(engine)
    app.dependency_overrides[get_response_executor] = FakeResponseExecutor
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_response = await client.post(
                "/api/v1/conversations",
                json={"title": "测试会话"},
            )
            assert create_response.status_code == 201
            conversation_id = create_response.json()["id"]

            send_response = await client.post(
                f"/api/v1/conversations/{conversation_id}/messages",
                json={"content": "你好"},
            )

            assert send_response.status_code == 200
            messages = send_response.json()["messages"]
            assert [message["role"] for message in messages] == ["user", "assistant"]
            assert messages[1]["content"] == "收到你的消息：你好"
    finally:
        app.dependency_overrides.pop(get_response_executor, None)


async def test_stream_message_returns_deltas_and_completed_conversation() -> None:
    await create_tables(engine)
    app.dependency_overrides[get_response_executor] = FakeResponseExecutor
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            create_response = await client.post(
                "/api/v1/conversations",
                json={"title": "流式测试"},
            )
            conversation_id = create_response.json()["id"]

            response = await client.post(
                f"/api/v1/conversations/{conversation_id}/messages/stream",
                json={"content": "你好"},
            )

            assert response.status_code == 200
            assert response.headers["content-type"].startswith("text/event-stream")
            assert "event: delta" in response.text
            assert 'data: {"content": "收到你的消息：你好"}' in response.text
            assert "event: completed" in response.text

            detail_response = await client.get(f"/api/v1/conversations/{conversation_id}")
            messages = detail_response.json()["messages"]
            assert [message["role"] for message in messages] == ["user", "assistant"]
            assert messages[1]["content"] == "收到你的消息：你好"
    finally:
        app.dependency_overrides.pop(get_response_executor, None)
