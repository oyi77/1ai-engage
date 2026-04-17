"""Abstract repository interface for Lead data access."""

from abc import ABC, abstractmethod
from typing import List, Optional

from oneai_reach.domain.models.lead import Lead, LeadStatus


class LeadRepository(ABC):
    """Abstract repository for Lead data access.

    Defines the contract for all lead persistence operations.
    Implementations must handle CSV, SQLite, or other storage backends.
    """

    @abstractmethod
    def get_by_id(self, lead_id: str) -> Optional[Lead]:
        """Get lead by ID.

        Args:
            lead_id: Unique lead identifier

        Returns:
            Lead object if found, None otherwise
        """
        pass

    @abstractmethod
    def get_all(self) -> List[Lead]:
        """Get all leads.

        Returns:
            List of all Lead objects
        """
        pass

    @abstractmethod
    def save(self, lead: Lead) -> Lead:
        """Save new lead.

        Args:
            lead: Lead object to save (should not have ID set)

        Returns:
            Saved Lead object with ID assigned

        Raises:
            ValueError: If lead already has an ID
        """
        pass

    @abstractmethod
    def update(self, lead: Lead) -> Lead:
        """Update existing lead.

        Args:
            lead: Lead object with ID set and updated fields

        Returns:
            Updated Lead object

        Raises:
            ValueError: If lead ID not found
        """
        pass

    @abstractmethod
    def delete(self, lead_id: str) -> bool:
        """Delete lead by ID.

        Args:
            lead_id: Unique lead identifier

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    def find_by_status(self, status: LeadStatus) -> List[Lead]:
        """Find leads by status.

        Args:
            status: LeadStatus enum value to filter by

        Returns:
            List of Lead objects with matching status
        """
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Lead]:
        """Find lead by email address.

        Args:
            email: Email address to search for

        Returns:
            Lead object if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_phone(self, phone: str) -> Optional[Lead]:
        """Find lead by phone number.

        Args:
            phone: Phone number to search for (normalized format)

        Returns:
            Lead object if found, None otherwise
        """
        pass

    @abstractmethod
    def find_by_website(self, website: str) -> Optional[Lead]:
        """Find lead by website URL.

        Args:
            website: Website URL to search for

        Returns:
            Lead object if found, None otherwise
        """
        pass

    @abstractmethod
    def find_warm_leads(self) -> List[Lead]:
        """Find all warm leads (replied or meeting booked).

        Returns:
            List of warm Lead objects
        """
        pass

    @abstractmethod
    def find_cold_leads(self) -> List[Lead]:
        """Find all cold leads (cold, lost, or unsubscribed).

        Returns:
            List of cold Lead objects
        """
        pass

    @abstractmethod
    def find_needs_followup(self) -> List[Lead]:
        """Find leads that need follow-up.

        Returns:
            List of Lead objects requiring follow-up
        """
        pass

    @abstractmethod
    def count_by_status(self) -> dict[LeadStatus, int]:
        """Count leads by status.

        Returns:
            Dictionary mapping LeadStatus to count
        """
        pass

    @abstractmethod
    def search(self, query: str) -> List[Lead]:
        """Search leads by name, email, or company.

        Args:
            query: Search query string

        Returns:
            List of matching Lead objects
        """
        pass
