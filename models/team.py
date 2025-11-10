
from typing import List, Optional

from services.storage import load_team_txt, save_team_txt, list_team_names_for_department

class Team:
    """
    Team belongs to a department (by name) and stores members as names.
    Persisted to data/teams/<team_name>.txt (one name per line).
    """
    def __init__(self, name: str, department_name: str, members: Optional[List[str]] = None):
        self.name = name
        self.department_name = department_name
        self.members: List[str] = members or []

    @classmethod
    def load(cls, team_name: str, department_name: str) -> "Team":
        members = load_team_txt(cls._full_team_key(team_name, department_name))
        return cls(name=team_name, department_name=department_name, members=members)

    def save(self) -> None:
        save_team_txt(self._full_team_key(self.name, self.department_name), self.members)

    def add_member(self, member_name: str) -> bool:
        """Add if not already present (case-insensitive check). Returns True if added."""
        key = member_name.casefold()
        if any(m.casefold() == key for m in self.members):
            return False
        self.members.append(member_name)
        return True

    def list_members(self) -> list[str]:
        return list(self.members)

    @staticmethod
    def _full_team_key(team_name: str, department_name: str) -> str:
        return f"{department_name}_{team_name}"

    @staticmethod
    def list_for_department(department_name: str) -> list[str]:
        return list_team_names_for_department(department_name)