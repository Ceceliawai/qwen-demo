from collections.abc import AsyncIterator
from dataclasses import dataclass
from uuid import UUID

from modules.conversation.application.errors import ConversationNotFoundError
from modules.conversation.domain.conversation import Conversation
from modules.conversation.domain.message import MessageRole
from modules.conversation.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from modules.execution.application.response_executor import (
    ExecutionRequest,
    ResponseExecutor,
)


@dataclass(frozen=True, slots=True)
class CreateConversationCommand:
    title: str | None = None
    project_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class MessageDelta:
    content: str


@dataclass(frozen=True, slots=True)
class MessageCompleted:
    conversation: Conversation


type SendMessageStreamEvent = MessageDelta | MessageCompleted


class CreateConversation:
    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository

    async def execute(self, command: CreateConversationCommand) -> Conversation:
        conversation = Conversation.create(title=command.title, project_id=command.project_id)
        await self._repository.save(conversation)
        return conversation


class ListConversations:
    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[Conversation]:
        return await self._repository.list()


class GetConversation:
    def __init__(self, repository: ConversationRepository) -> None:
        self._repository = repository

    async def execute(self, conversation_id: UUID) -> Conversation:
        conversation = await self._repository.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)
        return conversation


class SendMessage:
    def __init__(
        self,
        repository: ConversationRepository,
        executor: ResponseExecutor,
    ) -> None:
        self._repository = repository
        self._executor = executor

    async def execute(self, conversation_id: UUID, content: str) -> Conversation:
        conversation = await self._repository.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        user_message = conversation.add_message(MessageRole.USER, content)
        history = tuple(
            {"role": message.role.value, "content": message.content}
            for message in conversation.messages
            if message.id != user_message.id
        )
        result = await self._executor.execute(
            ExecutionRequest(
                conversation_id=conversation.id,
                user_content=user_message.content,
                history=history,
            )
        )
        conversation.add_message(MessageRole.ASSISTANT, result.content)
        await self._repository.save(conversation)
        return conversation

    async def stream(
        self, conversation_id: UUID, content: str
    ) -> AsyncIterator[SendMessageStreamEvent]:
        conversation = await self._repository.get(conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(conversation_id)

        user_message = conversation.add_message(MessageRole.USER, content)
        history = tuple(
            {"role": message.role.value, "content": message.content}
            for message in conversation.messages
            if message.id != user_message.id
        )
        await self._repository.save(conversation)

        chunks: list[str] = []
        async for chunk in self._executor.stream(
            ExecutionRequest(
                conversation_id=conversation.id,
                user_content=user_message.content,
                history=history,
            )
        ):
            chunks.append(chunk)
            yield MessageDelta(content=chunk)

        conversation.add_message(MessageRole.ASSISTANT, "".join(chunks))
        await self._repository.save(conversation)
        yield MessageCompleted(conversation=conversation)
