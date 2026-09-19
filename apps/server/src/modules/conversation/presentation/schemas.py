from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from modules.conversation.domain.conversation import Conversation
from modules.conversation.domain.message import Message


class CreateConversationRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    project_id: UUID | None = None


class SendMessageRequest(BaseModel):
    content: str = Field(min_length=1, max_length=100_000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    sequence: int
    status: str
    created_at: datetime

    @classmethod
    def from_domain(cls, message: Message) -> "MessageResponse":
        return cls(
            id=message.id,
            conversation_id=message.conversation_id,
            role=message.role.value,
            content=message.content,
            sequence=message.sequence,
            status=message.status.value,
            created_at=message.created_at,
        )


class ConversationResponse(BaseModel):
    id: UUID
    title: str
    project_id: UUID | None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)

    @classmethod
    def from_domain(cls, conversation: Conversation) -> "ConversationResponse":
        return cls(
            id=conversation.id,
            title=conversation.title,
            project_id=conversation.project_id,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at,
            messages=[MessageResponse.from_domain(message) for message in conversation.messages],
        )
