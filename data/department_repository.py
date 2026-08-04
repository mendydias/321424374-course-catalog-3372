from models import Department

_DEPARTMENTS: dict[str, Department] = {
    "EE": Department(code="EE", name="Electrical and Computer Engineering"),
}


def get_department(code: str) -> Department | None:
    return _DEPARTMENTS.get(code.upper())


def add_department(code: str, name: str) -> None:
    code = code.upper()
    if code in _DEPARTMENTS:
        raise ValueError(f"Department code '{code}' already exists")
    _DEPARTMENTS[code] = Department(code=code, name=name)


def update_department(code: str, name: str) -> None:
    code = code.upper()
    if code not in _DEPARTMENTS:
        raise ValueError(f"Department code '{code}' not found")
    _DEPARTMENTS[code] = Department(code=code, name=name)


def remove_department(code: str) -> None:
    code = code.upper()
    if code not in _DEPARTMENTS:
        raise ValueError(f"Department code '{code}' not found")
    del _DEPARTMENTS[code]


def list_departments() -> dict[str, Department]:
    return dict(_DEPARTMENTS)
