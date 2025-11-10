from typing import List,Optional
from models.employee import Employee
from services.storage import load_department_txt, save_department_txt

class Department:
    def __init__(self, name: str, employees: Optional[List[Employee]] = None):
        self.name = name
        self.employees: List[Employee] = employees or []
        
    @classmethod
    def load(cls, name: str) -> 'Department':
        rows = load_department_txt(name)
        employees = [Employee(n, p, s) for (n, p, s) in rows]
        return cls(name, employees)
    
    def save(self)-> None:
        save_department_txt(self.name, self.employees)
        
    def add_employee(self, employee: Employee, logger = None) -> None:
        self.employees.append(employee)
        if logger:
            logger.info(f"Added employee: {employee}")
    
    def list_employees(self) -> list[tuple[str, str, float]]:
        """Return a simple view for terminal output."""
        return [(e.name, e.position, e.salary) for e in self.employees]

    def increase_salary_by_name(self, name: str, amount: float, logger = None) -> bool:
        key = name.casefold()
        for e in self.employees:
            if e.name.casefold() == key:
                e.increase_salary(amount, logger=logger)
                if logger: (f"[Department {self.name}] Persisting salary change for {e.name}")
                return True
        return False