from pathlib import Path
import re

DATA_ROOT = Path("data")

def ensure_dirs():
    (DATA_ROOT / "departments").mkdir(parents=True, exist_ok=True)
    (DATA_ROOT / "teams").mkdir(parents=True, exist_ok=True)

def safe_name(s: str) -> str:
    """
    Make a filesystem-safe name:
    - trim whitespace
    - replace any non [A-Za-z0-9_-] with underscore
    - collapse repeats naturally via regex
    """
    s = s.strip()
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s)
# --- TXT storage for departments (employees) ---

def dept_file(department_name: str) -> Path:
    safe = department_name.replace(" ", "_")
    return DATA_ROOT / "departments" / f"{safe}.txt"

def save_department_txt(department_name: str, employees: list) -> None:
    """
    employees: list[Employee]  -> writes 'name|position|salary' per line
    """
    path = dept_file(department_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("name|position|salary\n")
        for e in employees:
            f.write(f"{e.name}|{e.position}|{e.salary}\n")

def load_department_txt(department_name: str) -> list[tuple[str, str, float]]:
    """
    Returns list of tuples: (name, position, salary)
    """
    path = dept_file(department_name)
    if not path.exists():
        return []
    rows = []
    with path.open("r", encoding="utf-8") as f:
        header = f.readline()  # discard header
        for line in f:
            line = line.strip()
            if not line:
                continue
            name, position, salary = line.split("|")
            rows.append((name, position, float(salary)))
    return rows

def team_file(team_name: str) -> Path:
    safe = team_name.replace(" ", "_")
    return DATA_ROOT / "teams" / f"{safe}.txt"

def save_team_txt(team_name: str, members: list[str]) -> None:
    path = team_file(team_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for m in members:
            f.write(f"{m}\n")

def load_team_txt(team_name: str) -> list[str]:
    path = team_file(team_name)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
    
def team_file_for(department_name: str, team_name: str) -> Path:
    return DATA_ROOT / "teams" / f"{safe_name(department_name)}__{safe_name(team_name)}.txt"

def save_team_txt_for(department_name: str, team_name: str, members: list[str]) -> None:
    path = team_file_for(department_name, team_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for m in members:
            f.write(f"{m}\n")

def load_team_txt_for(department_name: str, team_name: str) -> list[str]:
    path = team_file_for(department_name, team_name)
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def list_team_names_for_department(department_name: str) -> list[str]:
    teams_dir = DATA_ROOT / "teams"
    if not teams_dir.exists():
        return []
    prefix = f"{safe_name(department_name)}__"
    names = []
    for p in teams_dir.glob(f"{prefix}*.txt"):
        # "<Dept>__<Team>.txt" -> "<Team>"
        t = p.stem[len(prefix):].replace("_", " ")
        names.append(t)
    return sorted(names, key=str.casefold)

def manager_file(manager_name: str) -> Path:
    safe = manager_name.replace(" ", "_")
    return DATA_ROOT / "managers" / f"{safe}.txt"

def save_manager_txt(manager_name: str, position: str, salary: float, direct_reports: list[str]) -> None:
    path = manager_file(manager_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("name|position|salary\n")
        f.write(f"{manager_name}|{position}|{salary:.2f}\n")
        f.write("--direct_reports--\n")
        for r in direct_reports:
            f.write(f"{r}\n")

def load_manager_txt(manager_name: str) -> tuple[str, str, float, list[str]] | None:
    path = manager_file(manager_name)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines or not lines[0].lower().startswith("name|position|salary"):
        return None
    # row with data
    name, position, salary = lines[1].split("|")
    # find marker direct reports
    try:
        idx = lines.index("--direct_reports--")
        reports = lines[idx+1:]
    except ValueError:
        reports = []
    return name, position, float(salary), reports

def list_manager_names() -> list[str]:
    mgr_dir = DATA_ROOT / "managers"
    if not mgr_dir.exists():
        return []
    return sorted([p.stem.replace("_", " ") for p in mgr_dir.glob("*.txt")], key=str.casefold)

def director_file(director_name: str) -> Path:
    safe = director_name.replace(" ", "_")
    return DATA_ROOT / "directors" / f"{safe}.txt"

def save_director_txt(director_name: str, position: str, salary: float,
                      departments: list[str], direct_reports: list[str]) -> None:
    path = director_file(director_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("name|position|salary\n")
        f.write(f"{director_name}|{position}|{salary:.2f}\n")
        f.write("--departments--\n")
        for d in departments:
            f.write(f"{d}\n")
        f.write("--direct_reports--\n")
        for r in direct_reports:
            f.write(f"{r}\n")

def load_director_txt(director_name: str) -> tuple[str, str, float, list[str], list[str]] | None:
    path = director_file(director_name)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    if not lines or not lines[0].lower().startswith("name|position|salary"):
        return None

    try:
        d_name, position, salary = lines[1].split("|")
        salary = float(salary)
    except Exception:
        return None

    depts: list[str] = []
    reports: list[str] = []

    try:
        idx_depts = lines.index("--departments--")
    except ValueError:
        idx_depts = -1
    try:
        idx_reports = lines.index("--direct_reports--")
    except ValueError:
        idx_reports = -1

    if idx_depts != -1 and idx_reports != -1:
        depts = lines[idx_depts + 1:idx_reports]
        reports = lines[idx_reports + 1:]
    elif idx_depts != -1:
        depts = lines[idx_depts + 1:]
    elif idx_reports != -1:
        reports = lines[idx_reports + 1:]

    return d_name, position, salary, depts, reports

def list_director_names() -> list[str]:
    ddir = DATA_ROOT / "directors"
    if not ddir.exists():
        return []
    return sorted([p.stem.replace("_", " ") for p in ddir.glob("*.txt")], key=str.casefold)

