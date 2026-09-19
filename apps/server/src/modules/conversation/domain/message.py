from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID

from shared.ids import new_id


class MessageRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageStatus(StrEnum):
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Message:
    id: UUID
    conversation_id: UUID
    role: MessageRole
    content: str
    sequence: int
    created_at: datetime
    status: MessageStatus = MessageStatus.COMPLETED

    @classmethod
    def create(
        cls,
        conversation_id: UUID,
        role: MessageRole,
        content: str,
        sequence: int,
        *,
        message_id: UUID | None = None,
        created_at: datetime | None = None,
        status: MessageStatus = MessageStatus.COMPLETED,
    ) -> "Message":
        normalized_content = content.strip()
        if not normalized_content:
            raise ValueError("消息内容不能为空")
        if sequence < 0:
            raise ValueError("消息序号不能小于 0")

        return cls(
            id=message_id or new_id(),
            conversation_id=conversation_id,
            role=role,
            content=normalized_content,
            sequence=sequence,
            created_at=created_at or datetime.now(UTC),
            status=status,
        )
