from httpx import ASGITransport, AsyncClient

from bootstrap.database.init import create_tables
from bootstrap.database.session import engine
from main import app


async def test_create_and_send_message() -> None:
    await create_tables(engine)
    transport = ASGITransport(app=app)
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
