from typing import List, Optional, Iterable
from models.manager import Manager
from models.department import Department
from services.storage import save_director_txt, load_director_txt

class Director(Manager):
    def __init__(
        self,
        name: str,
        position: str,
        salary: float,
        direct_reports: Optional[List[str]] = None,
        departments: Optional[List[str]] = None,
    ):
        super().__init__(name, position, salary, direct_reports=direct_reports)
        self._departments: List[str] = departments or []

    def save(self) -> None:
        """Persist director with departments and direct reports."""
        save_director_txt(
            self.name,
            self.position,
            self.salary,
            self._departments,
            list(self._direct_reports),
        )

    @classmethod
    def load(cls, name: str) -> Director | None:
        row = load_director_txt(name)
        if row is None:
            return None
        d_name, position, salary, depts, reports = row
        return cls(d_name, position, salary, direct_reports=reports, departments=depts)

    def assign_department(self, department: Department, logger=None) -> None:
        key = department.name.casefold()
        if not any(d.casefold() == key for d in self._departments):
            self._departments.append(department.name)
            if logger:
                logger.info(f"[Director {self.name}] Assigned department: {department.name}")

    def list_departments(self) -> Iterable[str]:
        return list(self._departments)

    def make_decision(self, text: str, departments: Optional[List[Department]] = None, logger=None) -> None:
        affected = ", ".join(self._departments) if departments is None else ", ".join(d.name for d in departments) or "(empty list)"
        if logger:
            logger.info(f"[Director {self.name}] Decision: '{text}' | Affected: {affected}")