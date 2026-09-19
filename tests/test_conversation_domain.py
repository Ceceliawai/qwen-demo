from modules.conversation.domain.conversation import Conversation
from modules.conversation.domain.message import MessageRole


def test_conversation_assigns_ordered_messages() -> None:
    conversation = Conversation.create("测试会话")

    first = conversation.add_message(MessageRole.USER, "你好")
    second = conversation.add_message(MessageRole.ASSISTANT, "你好，有什么可以帮你？")

    assert first.sequence == 0
    assert second.sequence == 1
    assert [message.role for message in conversation.messages] == [
        MessageRole.USER,
        MessageRole.ASSISTANT,
    ]
