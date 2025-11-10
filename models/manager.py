from typing import List, Iterable, Optional
from models.employee import Employee
from models.department import Department
from services.storage import save_manager_txt, load_manager_txt

class Manager(Employee):
    def __init__(self, name: str, position: str, salary: float, direct_reports: Optional[List[str]] = None):
        super().__init__(name, position, salary)
        self._direct_reports: List[str] = direct_reports or []

    # --- Persistence ---
    def save(self) -> None:
        save_manager_txt(self.name, self.position, self.salary, self._direct_reports)

    @classmethod
    def load(cls, name: str) -> "Manager | None"  :
        row = load_manager_txt(name)
        if row is None:
            return None
        mgr_name, position, salary, reports = row
        return cls(mgr_name, position, salary, direct_reports=reports)

    # --- People management (ostáva ako máš) ---
    def hire_employee(self, department: Department, employee: Employee, logger=None) -> None:
        department.add_employee(employee, logger=logger)
        department.save()
        if logger:
            logger.info(f"[Manager {self.name}] Hired {employee.name} into Department {department.name}")

    def add_direct_report(self, employee_name: str, logger=None) -> None:
        key = employee_name.casefold()
        if not any(n.casefold() == key for n in self._direct_reports):
            self._direct_reports.append(employee_name)
            if logger:
                logger.info(f"[Manager {self.name}] Added direct report: {employee_name}")
