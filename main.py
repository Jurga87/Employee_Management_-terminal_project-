from pathlib import Path
from typing import Optional
from services.logger import get_logger
from services.storage import (ensure_dirs, 
list_manager_names, list_director_names)
from models.employee import Employee
from models.department import Department
from models.manager import Manager
from models.director import Director
from models.team import Team

DEPT_DIR = Path("data/departments")


def list_department_names() -> list[str]:
    """Return department names inferred from TXT files in data/departments."""
    if not DEPT_DIR.exists():
        return []
    names = []
    for p in DEPT_DIR.glob("*.txt"):
        # file 'IT.txt' -> name 'IT'
        names.append(p.stem.replace("_", " "))
    return sorted(names, key=str.casefold)

def select_or_create_department() -> Department:
    """Interactive selector that loads or creates a department by name."""
    existing = list_department_names()
    if existing:
        print("\nAvailable departments:")
        for i, name in enumerate(existing, start=1):
            print(f"{i}) {name}")
        print("0) Create new department")
    else:
        print("\nNo departments found. You'll need to create one.")

    choice = input("Select number (or 0 to create new): ").strip()
    if existing and choice.isdigit() and int(choice) in range(1, len(existing) + 1):
        return Department.load(existing[int(choice) - 1])

    # Create new
    new_name = input("Enter new department name: ").strip()
    if not new_name:
        print("Invalid department name. Falling back to 'IT'.")
        new_name = "IT"
    # Department.load() returns empty if file not exists 
    return Department.load(new_name)

def add_employee_flow(dept: Department, logger):
    name = input("Enter name: ").strip()
    position = input("Enter position: ").strip()

    salary_str = input("Enter salary: ").strip()
    try:
        salary = float(salary_str)
        if salary <= 0:
            print("Salary must be positive.")
            return
    except ValueError:
        print("Invalid salary number.")
        return

    emp = Employee(name, position, salary)
    dept.add_employee(emp, logger=logger)
    dept.save()
    print(f"Employee {name} added to department {dept.name}.")

def list_employees_flow(dept: Department):
    rows = dept.list_employees()
    if not rows:
        print(f"No employees in {dept.name}.")
        return
    print(f"Employees in {dept.name}:")
    for (n, p, s) in rows:
        print(f"- {n} | {p} | {s}")

def increase_salary_flow(dept: Department, logger):
    if not dept.employees:
        print(f"No employees in {dept.name}.")
        return

    name = input("Employee name: ").strip()
    amount_str = input("Increase amount: ").strip()
    try:
        amount = float(amount_str)
        if amount <= 0:
            print("Amount must be positive.")
            return
    except ValueError:
        print("Invalid amount.")
        return

    updated = dept.increase_salary_by_name(name, amount, logger=logger)
    if not updated:
        print(f"Employee '{name}' not found.")
        return

    dept.save()
    print(f"Salary increased for {name} by {amount}.")
    
def manager_add_employee_flow(dept: Department, logger):
    print(f"\n[Manager flow] Department: {dept.name}")
    # Create a temporary manager (later we can persist managers too)
    mgr_name = input("Manager name: ").strip()
    mgr_position = "Manager"
    mgr_salary_str = input("Manager salary: ").strip()
    try:
        mgr_salary = float(mgr_salary_str)
        if mgr_salary <= 0:
            print("Manager salary must be positive.")
            return
    except ValueError:
        print("Invalid manager salary.")
        return
    
def create_manager_flow(logger) -> Manager:
    print("\n=== Create Manager ===")
    name = input("Manager name: ").strip()
    position = input("Manager position: ").strip() or "Manager"
    while True:
        s = input("Manager salary: ").strip()
        try:
            salary = float(s)
            if salary <= 0:
                print("Salary must be positive.")
                continue
            break
        except ValueError:
            print("Invalid number.")
    m = Manager(name, position, salary)
    m.save()  # NEW: persist immediately
    if logger:
        logger.info(f"Created manager: {m}")
    print(f"Manager {name} created and saved.")
    return m

def load_manager_flow() -> Manager | None:
    names = list_manager_names()
    if not names:
        print("No managers saved yet.")
        return None
    print("\nSaved managers:")
    for i, n in enumerate(names, start=1):
        print(f"{i}) {n}")
    choice = input("Select number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print("Invalid selection.")
        return None
    mgr = Manager.load(names[int(choice)-1])
    if mgr is None:
        print("Failed to load manager.")
    else:
        print(f"Loaded manager: {mgr.name}")
    return mgr

def manager_hire_flow(manager: Optional[Manager], dept: Department, logger):
    if manager is None:
        print("No manager is active. Create one first (option 4).")
        return

    print(f"\n=== {manager.name} hires into {dept.name} ===")
    name = input("New employee name: ").strip()
    position = input("Position: ").strip()

    while True:
        s = input("Salary: ").strip()
        try:
            salary = float(s)
            if salary <= 0:
                print("Salary must be positive.")
                continue
            break
        except ValueError:
            print("Invalid number.")
    
def create_director_flow(logger) -> Director:
    print("\n=== Create Director ===")
    name = input("Director name: ").strip()
    position = input("Director position: ").strip() or "Director"
    while True:
        s = input("Director salary: ").strip()
        try:
            salary = float(s)
            if salary <= 0:
                print("Salary must be positive.")
                continue
            break
        except ValueError:
            print("Invalid number.")
    d = Director(name, position, salary)
    d.save()  # persist immediately
    if logger:
        logger.info(f"Created director: {d}")
    print(f"Director {name} created and saved.")
    return d

def director_assign_current_department_flow(director: Optional[Director], dept: Department, logger):
    if director is None:
        print("No director is active. Create one first.")
        return
    director.assign_department(dept, logger=logger)
    print(f"Assigned department '{dept.name}' to director {director.name}.")

def director_make_decision_flow(director: Optional[Director], current_dept: Department, logger):
    if director is None:
        print("No director is active. Create one first.")
        return
    print("\n=== Director Decision ===")
    text = input("Decision text: ").strip()
    scope = input("Apply to (C)urrent dept or (A)ll assigned? [C/A]: ").strip().lower()
    if scope == "c":
        director.make_decision(text, departments=[current_dept], logger=logger)
        print(f"Decision logged for department {current_dept.name}.")
    else:
        director.make_decision(text, departments=None, logger=logger)  # uses assigned list
        print(f"Decision logged for director's assigned departments: {', '.join(director.list_departments()) or '(none)'}")

    # emp = Employee(name, position, salary)
    # manager.hire_employee(dept, emp, logger=logger)
    # manager.add_direct_report(emp.name, logger=logger)  # optional tracking
    # print(f"{emp.name} hired into {dept.name} by {manager.name}.")

def load_director_flow() -> Director | None:
    names = list_director_names()
    if not names:
        print("No directors saved yet.")
        return None
    print("\nSaved directors:")
    for i, n in enumerate(names, start=1):
        print(f"{i}) {n}")
    choice = input("Select number: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(names)):
        print("Invalid selection.")
        return None
    d = Director.load(names[int(choice)-1])
    if d is None:
        print("Failed to load director.")
        return None
    print(f"Loaded director: {d.name}")
    return d

def save_current_director_flow(director: Director | None):
    if director is None:
        print("No director is active.")
        return
    director.save()
    print(f"Director {director.name} saved.")

def create_team_flow(dept: Department, logger):
    print("\n=== Create Team ===")
    team_name = input("Team name: ").strip()
    if not team_name:
        print("Team name cannot be empty.")
        return
    team = Team.load(dept.name, team_name)  # if not exists, load() returns empty team
    # if already has file/members, it's effectively existing; still fine to "recreate"
    team.save()
    if logger:
        logger.info(f"[Department {dept.name}] Created/Ensured team file: {team_name}")
    print(f"Team '{team_name}' is ready in department '{dept.name}'.")

def list_teams_flow(dept: Department):
    teams = Team.list_for_department(dept.name)
    if not teams:
        print(f"No teams in {dept.name}.")
        return
    print(f"Teams in {dept.name}:")
    for t in teams:
        print(f"- {t}")

def main():
    ensure_dirs()
    logger = get_logger()
    dept = select_or_create_department()
    current_manager = None
    current_director = None 
    

    while True:
        print("\n=== Skllimea — Employee Management ===")
        print(f"[Department: {dept.name}]")
        print("1) Add employee")
        print("2) Increase salary")
        print("3) List employees")
        print("4) Create manager")
        print("5) Manager hires employee")
        print("6) Load manager")
        print("7) Save current manager")
        print("8) Create director")                  
        print("9) Change department")
        print("10) Director: assign CURRENT dept")    
        print("11) Director: make decision")
        print("12) Load director")         
        print("13) Save current director") 
        print("0) Exit")
        choice = input("Select: ").strip()

        if choice == "1":
            add_employee_flow(dept, logger)
            
        elif choice == "2":
            increase_salary_flow(dept, logger)
            
        elif choice == "3":
            list_employees_flow(dept)
            
        elif choice == "4":
            current_manager = create_manager_flow(logger)
            
        elif choice == "5":
            manager_hire_flow(current_manager, dept, logger)
            if current_manager:
                current_manager.save()  # persist reports after hire
                
        elif choice == "6":
            loaded = load_manager_flow()
            if loaded:
                current_manager = loaded
                
        elif choice == "7":
            if current_manager:
                current_manager.save()
                print(f"Manager {current_manager.name} saved.")
            else:
                print("No manager is active.")
                
        elif choice == "8":
            current_director = create_director_flow(logger)
            
        elif choice == "9":
            dept = select_or_create_department()
            
        elif choice == "10":
            director_assign_current_department_flow(current_director, dept, logger)
            
        elif choice == "11":
            director_make_decision_flow(current_director, dept, logger)
            
        elif choice == "12":
            loaded = load_director_flow()
            if loaded:
                current_director = loaded
        elif choice == "13":
            save_current_director_flow(current_director)
            
        elif choice == "0":
            print("Bye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()