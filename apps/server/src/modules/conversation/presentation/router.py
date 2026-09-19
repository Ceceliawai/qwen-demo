import json
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from bootstrap.container.execution import get_response_executor
from bootstrap.database.session import get_session
from modules.conversation.application.errors import ConversationNotFoundError
from modules.conversation.application.use_cases import (
    CreateConversation,
    CreateConversationCommand,
    GetConversation,
    ListConversations,
    MessageCompleted,
    MessageDelta,
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
from modules.execution.application.errors import (
    ResponseAuthenticationError,
    ResponseConfigurationError,
    ResponseRateLimitError,
    ResponseTimeoutError,
    ResponseUnavailableError,
)
from modules.execution.application.response_executor import ResponseExecutor

router = APIRouter(prefix="/conversations", tags=["conversations"])


async def _session_dependency() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


def _repository(session: AsyncSession) -> SqlAlchemyConversationRepository:
    return SqlAlchemyConversationRepository(session)


def _sse(event: str, data: object) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


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
    executor: ResponseExecutor = Depends(get_response_executor),  # noqa: B008
) -> ConversationResponse:
    try:
        conversation = await SendMessage(_repository(session), executor).execute(
            conversation_id, payload.content
        )
    except ConversationNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ResponseConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except ResponseAuthenticationError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    except ResponseRateLimitError as error:
        raise HTTPException(status_code=429, detail=str(error)) from error
    except ResponseTimeoutError as error:
        raise HTTPException(status_code=504, detail=str(error)) from error
    except ResponseUnavailableError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    return ConversationResponse.from_domain(conversation)


@router.post("/{conversation_id}/messages/stream")
async def stream_message(
    conversation_id: UUID,
    payload: SendMessageRequest,
    session: AsyncSession = Depends(_session_dependency),  # noqa: B008
    executor: ResponseExecutor = Depends(get_response_executor),  # noqa: B008
) -> StreamingResponse:
    async def events() -> AsyncIterator[str]:
        try:
            async for event in SendMessage(_repository(session), executor).stream(
                conversation_id, payload.content
            ):
                if isinstance(event, MessageDelta):
                    yield _sse("delta", {"content": event.content})
                elif isinstance(event, MessageCompleted):
                    response = ConversationResponse.from_domain(event.conversation)
                    yield _sse("completed", response.model_dump(mode="json"))
        except ConversationNotFoundError as error:
            yield _sse("error", {"detail": str(error), "code": "not_found"})
        except ResponseConfigurationError as error:
            yield _sse("error", {"detail": str(error), "code": "configuration"})
        except ResponseAuthenticationError as error:
            yield _sse("error", {"detail": str(error), "code": "authentication"})
        except ResponseRateLimitError as error:
            yield _sse("error", {"detail": str(error), "code": "rate_limit"})
        except ResponseTimeoutError as error:
            yield _sse("error", {"detail": str(error), "code": "timeout"})
        except ResponseUnavailableError as error:
            yield _sse("error", {"detail": str(error), "code": "unavailable"})

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
