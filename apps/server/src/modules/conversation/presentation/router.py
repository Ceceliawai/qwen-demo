from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.database.session import get_session
from modules.conversation.application.errors import ConversationNotFoundError
from modules.conversation.application.use_cases import (
    CreateConversation,
    CreateConversationCommand,
    GetConversation,
    ListConversations,
    SendMessage,
)
from modules.conversation.infrastructure.persistence.sqlalchemy_repository import (
    SqlAlchemyConversationRepository,
)
from modules.conversation.presentation.schemas import (
    ConversationResponse,
    CreateConversationRequest,
    SendMessageRequest,
)
from modules.execution.application.response_executor import FakeResponseExecutor

router = APIRouter(prefix="/conversations", tags=["conversations"])


async def _session_dependency() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


def _repository(session: AsyncSession) -> SqlAlchemyConversationRepository:
    return SqlAlchemyConversationRepository(session)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: CreateConversationRequest,
    session: AsyncSession = Depends(_session_dependency),  # noqa: B008
) -> ConversationResponse:
    conversation = await CreateConversation(_repository(session)).execute(
        CreateConversationCommand(title=payload.title, project_id=payload.project_id)
    )
    return ConversationResponse.from_domain(conversation)


@router.get("", response_model=list[ConversationResponse])
async def list_conversations(
    session: AsyncSession = Depends(_session_dependency),  # noqa: B008
) -> list[ConversationResponse]:
    conversations = await ListConversations(_repository(session)).execute()
    return [ConversationResponse.from_domain(item) for item in conversations]


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    session: AsyncSession = Depends(_session_dependency),  # noqa: B008
) -> ConversationResponse:
    try:
        conversation = await GetConversation(_repository(session)).execute(conversation_id)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return ConversationResponse.from_domain(conversation)


@router.post("/{conversation_id}/messages", response_model=ConversationResponse)
async def send_message(
    conversation_id: UUID,
    payload: SendMessageRequest,
    session: AsyncSession = Depends(_session_dependency),  # noqa: B008
) -> ConversationResponse:
    try:
        conversation = await SendMessage(
            _repository(session), FakeResponseExecutor()
        ).execute(conversation_id, payload.content)
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    return ConversationResponse.from_domain(conversation)
