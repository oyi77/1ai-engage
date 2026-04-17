"""Repository interfaces for data access abstraction."""

from oneai_reach.domain.repositories.lead_repository import LeadRepository
from oneai_reach.domain.repositories.conversation_repository import (
    ConversationRepository,
)
from oneai_reach.domain.repositories.knowledge_repository import KnowledgeRepository

__all__ = [
    "LeadRepository",
    "ConversationRepository",
    "KnowledgeRepository",
]
