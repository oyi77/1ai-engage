"""Abstract repository interface for Knowledge base data access."""

from abc import ABC, abstractmethod
from typing import List, Optional

from oneai_reach.domain.models.knowledge import KnowledgeEntry, KnowledgeCategory


class KnowledgeRepository(ABC):
    """Abstract repository for Knowledge base data access.

    Defines the contract for all knowledge base persistence operations.
    Implementations must handle SQLite with FTS5 or other storage backends.
    """

    @abstractmethod
    def get_by_id(self, entry_id: int) -> Optional[KnowledgeEntry]:
        """Get knowledge entry by ID.

        Args:
            entry_id: Unique entry identifier

        Returns:
            KnowledgeEntry object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self, wa_number_id: str) -> List[KnowledgeEntry]:
        """Get all knowledge entries for a WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            List of all KnowledgeEntry objects for this WA number
        """
        pass

    @abstractmethod
    def save(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Save new knowledge entry.

        Args:
            entry: KnowledgeEntry object to save (should not have ID set)

        Returns:
            Saved KnowledgeEntry object with ID assigned

        Raises:
            ValueError: If entry already has an ID
        """
        pass

    @abstractmethod
    def update(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        """Update existing knowledge entry.

        Args:
            entry: KnowledgeEntry object with ID set and updated fields

        Returns:
            Updated KnowledgeEntry object

        Raises:
            ValueError: If entry ID not found
        """
        pass

    @abstractmethod
    def delete(self, entry_id: int) -> bool:
        """Delete knowledge entry by ID.

        Args:
            entry_id: Unique entry identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def find_by_category(
        self, wa_number_id: str, category: KnowledgeCategory
    ) -> List[KnowledgeEntry]:
        """Find knowledge entries by category.

        Args:
            wa_number_id: WhatsApp number ID
            category: KnowledgeCategory enum value to filter by

        Returns:
            List of KnowledgeEntry objects with matching category
        """
        pass

    @abstractmethod
    def search(
        self, wa_number_id: str, query: str, limit: int = 5
    ) -> List[KnowledgeEntry]:
        """Full-text search knowledge entries.

        Args:
            wa_number_id: WhatsApp number ID
            query: Search query string
            limit: Maximum number of results (default: 5)

        Returns:
            List of matching KnowledgeEntry objects ranked by relevance
        """
        pass

    @abstractmethod
    def search_with_outcome_weighting(
        self, wa_number_id: str, query: str, limit: int = 5
    ) -> List[KnowledgeEntry]:
        """Search knowledge entries weighted by historical effectiveness.

        Args:
            wa_number_id: WhatsApp number ID
            query: Search query string
            limit: Maximum number of results (default: 5)

        Returns:
            List of matching KnowledgeEntry objects ranked by relevance and effectiveness
        """
        pass

    @abstractmethod
    def find_high_priority(self, wa_number_id: str) -> List[KnowledgeEntry]:
        """Find high-priority knowledge entries (priority >= 7).

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            List of high-priority KnowledgeEntry objects
        """
        pass

    @abstractmethod
    def find_by_tag(self, wa_number_id: str, tag: str) -> List[KnowledgeEntry]:
        """Find knowledge entries by tag.

        Args:
            wa_number_id: WhatsApp number ID
            tag: Tag to search for

        Returns:
            List of KnowledgeEntry objects with matching tag
        """
        pass

    @abstractmethod
    def find_learned_entries(
        self, wa_number_id: str, limit: int = 20
    ) -> List[KnowledgeEntry]:
        """Find auto-learned knowledge entries.

        Args:
            wa_number_id: WhatsApp number ID
            limit: Maximum number of results (default: 20)

        Returns:
            List of auto-learned KnowledgeEntry objects
        """
        pass

    @abstractmethod
    def count_by_category(self, wa_number_id: str) -> dict[KnowledgeCategory, int]:
        """Count knowledge entries by category.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            Dictionary mapping KnowledgeCategory to count
        """
        pass

    @abstractmethod
    def count_total(self, wa_number_id: str) -> int:
        """Count total knowledge entries for a WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            Total count of knowledge entries
        """
        pass

    @abstractmethod
    def import_entries(self, wa_number_id: str, entries: List[dict]) -> int:
        """Bulk-import knowledge entries.

        Args:
            wa_number_id: WhatsApp number ID
            entries: List of entry dicts with at least: category, question, answer

        Returns:
            Count of successfully imported entries
        """
        pass

    @abstractmethod
    def export_entries(self, wa_number_id: str) -> List[dict]:
        """Export all knowledge entries for a WA number.

        Args:
            wa_number_id: WhatsApp number ID

        Returns:
            List of entry dicts in portable format
        """
        pass
