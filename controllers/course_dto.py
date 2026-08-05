from dataclasses import dataclass

from models import Course


@dataclass
class CourseDTO:
    code: str
    department: str
    level: str
    credits: str
    name: str = ""
    semester: str = "0"
    lecturer: str = ""

    @classmethod
    def from_course(cls, course: Course) -> "CourseDTO":
        return cls(
            code=course.code,
            department=course.department.name,
            level=str(course.level),
            credits=str(course.credits),
            name=course.name,
            semester=str(course.semester),
            lecturer=course.lecturer,
        )
