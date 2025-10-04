"""File-based repository implementation for rule persistence."""

import json
import threading
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from application.ports import RuleRepository
from domain.models import Rule


class FileRuleRepository(RuleRepository):
    """Repository that persists rules to a JSON file."""

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._lock = threading.Lock()
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the rules file exists, create with empty list if not."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._write_rules([])

    def _read_rules(self) -> List[Rule]:
        """Read rules from file."""
        with self._lock:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Rule.from_dict(rule_data) for rule_data in data]

    def _write_rules(self, rules: List[Rule]) -> None:
        """Write rules to file."""
        with self._lock:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                data = [rule.to_dict() for rule in rules]
                json.dump(data, f, indent=2, ensure_ascii=False)

    def get_all(self) -> List[Rule]:
        """Retrieve all rules."""
        return self._read_rules()

    def get_by_id(self, rule_id: UUID) -> Optional[Rule]:
        """Retrieve a rule by its ID."""
        rules = self._read_rules()
        for rule in rules:
            if rule.id == rule_id:
                return rule
        return None

    def create(self, rule: Rule) -> Rule:
        """Create a new rule."""
        rules = self._read_rules()
        rules.append(rule)
        self._write_rules(rules)
        return rule

    def update(self, rule: Rule) -> Rule:
        """Update an existing rule."""
        rules = self._read_rules()
        updated = False

        for i, existing_rule in enumerate(rules):
            if existing_rule.id == rule.id:
                rules[i] = rule
                updated = True
                break

        if updated:
            self._write_rules(rules)

        return rule

    def delete(self, rule_id: UUID) -> bool:
        """Delete a rule by its ID."""
        rules = self._read_rules()
        initial_count = len(rules)
        rules = [rule for rule in rules if rule.id != rule_id]

        if len(rules) < initial_count:
            self._write_rules(rules)
            return True
        return False

    def save_all(self, rules: List[Rule]) -> None:
        """Save all rules to storage."""
        self._write_rules(rules)

