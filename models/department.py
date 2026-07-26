from dataclasses import dataclass


@dataclass(frozen=True)
class Department:
    code: str
    name: str
