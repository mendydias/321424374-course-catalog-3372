from dataclasses import dataclass

from models.department import Department


@dataclass
class Course:
    code: str
    department: Department
    level: int
    credits: int
    name: str = ""
    semester: int = 0
    lecturer: str = ""

    def __str__(self) -> str:
        return (
            f"{self.code} — {self.name or '(unnamed)'}\n"
            f"  Department: {self.department.name}\n"
            f"  Level:      {self.level}\n"
            f"  Credits:    {self.credits}\n"
            f"  Semester:   {self.semester}\n"
            f"  Lecturer:   {self.lecturer or '(none)'}"
        )

    def __repr__(self) -> str:
        return (
            f"Course(code={self.code!r}, department={self.department!r}, "
            f"level={self.level}, credits={self.credits}, name={self.name!r}, "
            f"semester={self.semester!r}, lecturer={self.lecturer!r})"
        )
