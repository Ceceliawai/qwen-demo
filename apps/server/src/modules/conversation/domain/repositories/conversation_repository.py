from typing import Protocol
from uuid import UUID

from modules.conversation.domain.conversation import Conversation


class ConversationRepository(Protocol):
    async def save(self, conversation: Conversation) -> None:
        ...

    async def get(self, conversation_id: UUID) -> Conversation | None:
        ...

    async def list(self) -> list[Conversation]:
        ...
