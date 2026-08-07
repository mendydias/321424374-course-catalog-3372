import pytest

from data import (
    add_department,
    get_department,
    list_departments,
    remove_department,
    update_department,
)
from data.department_repository import _DEPARTMENTS
from models import Department


@pytest.fixture(autouse=True)
def _isolate_departments():
    snapshot = dict(_DEPARTMENTS)
    yield
    _DEPARTMENTS.clear()
    _DEPARTMENTS.update(snapshot)


class TestGetDepartment:
    def test_get_existing_returns_department(self) -> None:
        assert get_department("EE") == Department(
            code="EE", name="Electrical and Computer Engineering"
        )

    def test_get_existing_is_case_insensitive(self) -> None:
        assert get_department("ee") == Department(
            code="EE", name="Electrical and Computer Engineering"
        )

    def test_get_nonexistent_returns_none(self) -> None:
        assert get_department("ZZ") is None


class TestAddDepartment:
    def test_add_new_department(self) -> None:
        add_department("cs", "Computer Science")
        assert get_department("CS") == Department(code="CS", name="Computer Science")

    def test_add_duplicate_raises_error(self) -> None:
        with pytest.raises(ValueError, match="already exists"):
            add_department("EE", "Duplicate")

    def test_add_duplicate_case_insensitive(self) -> None:
        with pytest.raises(ValueError, match="already exists"):
            add_department("ee", "Duplicate")


class TestUpdateDepartment:
    def test_update_existing_department(self) -> None:
        add_department("cs", "Computer Science")
        update_department("cs", "Computing Science")
        stored = get_department("CS")
        assert stored is not None
        assert stored.name == "Computing Science"

    def test_update_nonexistent_raises_error(self) -> None:
        with pytest.raises(ValueError, match="not found"):
            update_department("ZZ", "Zoology")


class TestRemoveDepartment:
    def test_remove_existing_department(self) -> None:
        add_department("cs", "Computer Science")
        remove_department("cs")
        assert get_department("CS") is None

    def test_remove_nonexistent_raises_error(self) -> None:
        with pytest.raises(ValueError, match="not found"):
            remove_department("ZZ")


class TestListDepartments:
    def test_list_departments_returns_copy(self) -> None:
        list_departments()["EE"] = None  # mutating the return must not affect the store
        assert get_department("EE") is not None

    def test_list_departments_includes_seeded_ee(self) -> None:
        assert "EE" in list_departments()
