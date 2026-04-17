"""Abstract repository interface for Conversation data access."""

from abc import ABC, abstractmethod
from typing import List, Optional

from oneai_reach.domain.models.conversation import (
    Conversation,
    ConversationStatus,
    EngineMode,
)


class ConversationRepository(ABC):
    """Abstract repository for Conversation data access.

    Defines the contract for all conversation persistence operations.
    Implementations must handle SQLite or other storage backends.
    """

    @abstractmethod
    def get_by_id(self, conversation_id: int) -> Optional[Conversation]:
        """Get conversation by ID.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            Conversation object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Conversation]:
        """Get all conversations.

        Returns:
            List of all Conversation objects
        """
        pass

    @abstractmethod
    def save(self, conversation: Conversation) -> Conversation:
        """Save new conversation.

        Args:
            conversation: Conversation object to save (should not have ID set)

        Returns:
            Saved Conversation object with ID assigned

        Raises:
            ValueError: If conversation already has an ID
        """
        pass

    @abstractmethod
    def update(self, conversation: Conversation) -> Conversation:
        """Update existing conversation.

        Args:
            conversation: Conversation object with ID set and updated fields

        Returns:
            Updated Conversation object

        Raises:
            ValueError: If conversation ID not found
        """
        pass

    @abstractmethod
    def delete(self, conversation_id: int) -> bool:
        """Delete conversation by ID.

        Args:
            conversation_id: Unique conversation identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def find_by_phone(
        self, wa_number_id: str, contact_phone: str
    ) -> Optional[Conversation]:
        """Find active conversation by WA number and contact phone.

        Args:
            wa_number_id: WhatsApp number ID
            contact_phone: Contact phone number

        Returns:
            Active Conversation object if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_status(self, status: ConversationStatus) -> List[Conversation]:
        """Find conversations by status.

        Args:
            status: ConversationStatus enum value to filter by

        Returns:
            List of Conversation objects with matching status
        """
        pass

    @abstractmethod
    def find_active(self, wa_number_id: Optional[str] = None) -> List[Conversation]:
        """Find all active conversations.

        Args:
            wa_number_id: Optional WA number ID to filter by

        Returns:
            List of active Conversation objects, ordered by last message time
        """
        pass

    @abstractmethod
    def find_by_lead_id(self, lead_id: str) -> List[Conversation]:
        """Find conversations linked to a lead.

        Args:
            lead_id: Lead ID to search for

        Returns:
            List of Conversation objects linked to the lead
        """
        pass

    @abstractmethod
    def find_stale(self, hours: int = 48) -> List[Conversation]:
        """Find stale conversations (inactive for specified hours).

        Args:
            hours: Hours of inactivity threshold (default: 48)

        Returns:
            List of stale active Conversation objects
        """
        pass

    @abstractmethod
    def find_by_engine_mode(self, engine_mode: EngineMode) -> List[Conversation]:
        """Find conversations by engine mode.

        Args:
            engine_mode: EngineMode enum value to filter by

        Returns:
            List of Conversation objects with matching engine mode
        """
        pass

    @abstractmethod
    def count_by_status(self) -> dict[ConversationStatus, int]:
        """Count conversations by status.

        Returns:
            Dictionary mapping ConversationStatus to count
        """
        pass

    @abstractmethod
    def count_by_wa_number(self, wa_number_id: str) -> int:
        """Count conversations for a specific WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            Count of conversations for this WA number
        """
        pass
