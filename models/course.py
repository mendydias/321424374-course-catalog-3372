from dataclasses import dataclass


@dataclass
class Course:
    code: str
    department: str
    level: int
    credits: int
    name: str = ""

    def __str__(self) -> str:
        return (
            f"{self.code} — {self.name or '(unnamed)'}\n"
            f"  Department: {self.department}\n"
            f"  Level:      {self.level}\n"
            f"  Credits:    {self.credits}"
        )

    def __repr__(self) -> str:
        return (
            f"Course(code={self.code!r}, department={self.department!r}, "
            f"level={self.level}, credits={self.credits}, name={self.name!r})"
        )
