"""Port interfaces defining contracts for external dependencies."""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.models import Rule


class RuleRepository(ABC):
    """Port interface for rule persistence."""

    @abstractmethod
    def get_all(self) -> List[Rule]:
        """Retrieve all rules."""
        pass

    @abstractmethod
    def get_by_id(self, rule_id: UUID) -> Optional[Rule]:
        """Retrieve a rule by its ID."""
        pass

    @abstractmethod
    def create(self, rule: Rule) -> Rule:
        """Create a new rule."""
        pass

    @abstractmethod
    def update(self, rule: Rule) -> Rule:
        """Update an existing rule."""
        pass

    @abstractmethod
    def delete(self, rule_id: UUID) -> bool:
        """Delete a rule by its ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def save_all(self, rules: List[Rule]) -> None:
        """Save all rules to storage."""
        pass

