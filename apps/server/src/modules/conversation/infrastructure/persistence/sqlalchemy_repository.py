from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from modules.conversation.domain.conversation import Conversation
from modules.conversation.domain.message import Message, MessageRole, MessageStatus
from modules.conversation.infrastructure.persistence.models import ConversationModel, MessageModel


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class SqlAlchemyConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, conversation: Conversation) -> None:
        model = await self._session.get(ConversationModel, str(conversation.id))
        if model is None:
            model = ConversationModel(id=str(conversation.id), title=conversation.title)
            self._session.add(model)

        model.title = conversation.title
        model.project_id = str(conversation.project_id) if conversation.project_id else None
        model.created_at = _utc(conversation.created_at)
        model.updated_at = _utc(conversation.updated_at)

        for message in conversation.messages:
            message_model = await self._session.get(MessageModel, str(message.id))
            if message_model is None:
                message_model = MessageModel(
                    id=str(message.id), conversation_id=str(conversation.id)
                )
                self._session.add(message_model)
            message_model.role = message.role.value
            message_model.content = message.content
            message_model.sequence = message.sequence
            message_model.status = message.status.value
            message_model.created_at = _utc(message.created_at)

        await self._session.commit()

    async def get(self, conversation_id: UUID) -> Conversation | None:
        result = await self._session.execute(
            select(ConversationModel).where(ConversationModel.id == str(conversation_id))
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None

        messages_result = await self._session.execute(
            select(MessageModel)
            .where(MessageModel.conversation_id == str(conversation_id))
            .order_by(MessageModel.sequence)
        )
        messages = [self._to_message(item) for item in messages_result.scalars()]
        return self._to_conversation(model, messages)

    async def list(self) -> list[Conversation]:
        result = await self._session.execute(
            select(ConversationModel).order_by(ConversationModel.updated_at.desc())
        )
        return [self._to_conversation(model, []) for model in result.scalars()]

    @staticmethod
    def _to_message(model: MessageModel) -> Message:
        return Message(
            id=UUID(model.id),
            conversation_id=UUID(model.conversation_id),
            role=MessageRole(model.role),
            content=model.content,
            sequence=model.sequence,
            status=MessageStatus(model.status),
            created_at=_utc(model.created_at),
        )

    @staticmethod
    def _to_conversation(model: ConversationModel, messages: list[Message]) -> Conversation:
        return Conversation(
            id=UUID(model.id),
            title=model.title,
            project_id=UUID(model.project_id) if model.project_id else None,
            created_at=_utc(model.created_at),
            updated_at=_utc(model.updated_at),
            messages=messages,
        )
