class Employee:
    def __init__(self, name: str, position: str, salary: float):
        self.name = name
        self.position = position
        self.salary = salary

    def increase_salary(self, amount: float, logger=None) -> None:
        if amount is None or amount <= 0:
            raise ValueError("Amount must be a positive number.")
        old = self.salary
        self.salary += amount
        if logger:
            logger.info(f"Salary increased: {self.name} from {old} to {self.salary} (+{amount})")

    def __repr__(self) -> str:
        return f"Employee(name={self.name}, position={self.position}, salary={self.salary})"
