from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from modules.conversation.domain.message import Message, MessageRole, MessageStatus
from shared.ids import new_id


@dataclass(slots=True)
class Conversation:
    id: UUID
    title: str
    project_id: UUID | None
    created_at: datetime
    updated_at: datetime
    messages: list[Message] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        title: str | None = None,
        *,
        conversation_id: UUID | None = None,
        project_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Conversation":
        now = created_at or datetime.now(UTC)
        normalized_title = (title or "新会话").strip() or "新会话"
        return cls(
            id=conversation_id or new_id(),
            title=normalized_title,
            project_id=project_id,
            created_at=now,
            updated_at=now,
        )

    def add_message(
        self,
        role: MessageRole,
        content: str,
        *,
        status: MessageStatus = MessageStatus.COMPLETED,
    ) -> Message:
        next_sequence = self.messages[-1].sequence + 1 if self.messages else 0
        message = Message.create(
            conversation_id=self.id,
            role=role,
            content=content,
            sequence=next_sequence,
            status=status,
        )
        self.messages.append(message)
        self.updated_at = datetime.now(UTC)
        return message
