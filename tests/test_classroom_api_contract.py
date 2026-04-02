# pyright: reportMissingImports=false

from uuid import UUID, uuid4
import os
import sys

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from db.enum import RoleEnum
from schemas.classroom import ClassLayoutItem, ClassroomResponse
from utils.app import app
from utils.auth_dep import get_current_user


class _DummyUser:
    def __init__(self) -> None:
        self.id = uuid4()
        self.role = RoleEnum.ADMIN


def _override_current_user() -> _DummyUser:
    return _DummyUser()


def _client() -> TestClient:
    app.dependency_overrides[get_current_user] = _override_current_user
    return TestClient(app)


def _cleanup_overrides() -> None:
    app.dependency_overrides.pop(get_current_user, None)


def test_classroom_list_includes_uuid_and_consistent_keys(monkeypatch):
    from api.v1 import classroom as classroom_api

    classroom_id = uuid4()
    payload = [
        ClassroomResponse(
            classroom_id=classroom_id,
            classroom_name="Class 1A",
            class_layout=[
                ClassLayoutItem(column_name="A", column_capacity=2, column_set="set_1")
            ],
            columns_count=1,
            max_rows=2,
            total_capacity=2,
            set_1_capacity=2,
            set_2_capacity=0,
        )
    ]

    monkeypatch.setattr(classroom_api, "list_classrooms", lambda: payload)

    client = _client()
    response = client.get("/api/v1/classroom/list")
    _cleanup_overrides()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    row = data[0]
    assert UUID(row["classroomId"]) == classroom_id

    expected_keys = {
        "classroomId",
        "classroomName",
        "classLayout",
        "columnsCount",
        "maxRows",
        "totalCapacity",
        "set1Capacity",
        "set2Capacity",
    }
    assert set(row.keys()) == expected_keys

    forbidden_aliases = {"id", "classroom_id", "classroom_name", "set_one_capacity"}
    assert forbidden_aliases.isdisjoint(row.keys())


def test_delete_works_with_classroom_id_from_list(monkeypatch):
    from api.v1 import classroom as classroom_api

    classroom_id = uuid4()

    def _mock_list_classrooms():
        return [
            ClassroomResponse(
                classroom_id=classroom_id,
                classroom_name="Class 1A",
                class_layout=[
                    ClassLayoutItem(column_name="A", column_capacity=2, column_set="set_1")
                ],
                columns_count=1,
                max_rows=2,
                total_capacity=2,
                set_1_capacity=2,
                set_2_capacity=0,
            )
        ]

    captured: dict[str, UUID] = {}

    def _mock_deactivate_classroom(classroom_id: UUID, actor_id):
        captured["classroom_id"] = classroom_id
        return {"message": "Classroom deleted successfully."}

    monkeypatch.setattr(classroom_api, "list_classrooms", _mock_list_classrooms)
    monkeypatch.setattr(classroom_api, "deactivate_classroom", _mock_deactivate_classroom)

    client = _client()
    list_response = client.get("/api/v1/classroom/list")
    assert list_response.status_code == 200

    listed_id = list_response.json()[0]["classroomId"]
    delete_response = client.delete(f"/api/v1/classroom/{listed_id}")
    _cleanup_overrides()

    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Classroom deleted successfully."
    assert captured["classroom_id"] == UUID(listed_id)


def test_delete_rejects_non_uuid_path_param():
    client = _client()
    response = client.delete("/api/v1/classroom/Class 1A")
    _cleanup_overrides()

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(item.get("type") == "uuid_parsing" for item in detail)


def test_update_rejects_non_uuid_path_param():
    client = _client()
    response = client.put(
        "/api/v1/classroom/Class 1A",
        json={
            "name": "Class 1A",
            "classLayout": [{"columnName": "A", "columnCapacity": 2, "columnSet": "set_1"}],
            "columnsCount": 1,
            "maxRows": 2,
            "totalCapacity": 2,
            "setOneCapacity": 2,
            "setTwoCapacity": 0,
        },
    )
    _cleanup_overrides()

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(item.get("type") == "uuid_parsing" for item in detail)
