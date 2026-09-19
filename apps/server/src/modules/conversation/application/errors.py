from uuid import UUID


class ConversationNotFoundError(LookupError):
    def __init__(self, conversation_id: UUID) -> None:
        super().__init__(f"Conversation not found: {conversation_id}")
        self.conversation_id = conversation_id
