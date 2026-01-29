from datetime import datetime
import pytest

pytest.importorskip("pymongo")

from src.domain.user import User, Role, Status
from src.domain.task import Task, TaskStatus, Priority
from src.domain.event import TaskEvent, EventType
from src.repo import mongo_repo as mr


def test_user_mapping_roundtrip():
    u = User(id="u1", email="a@b.com", role=Role.MANAGER, status=Status.BLOCKED)
    doc = mr._user_to_doc(u)
    got = mr._doc_to_user(doc)
    assert got == u


def test_task_mapping_roundtrip_all_fields():
    t = Task(
        id="t1",
        title="T",
        description="d",
        status=TaskStatus.IN_PROGRESS,
        priority=Priority.HIGH,
        owner_id="u1",
        assignee_id="u2",
        due_date=datetime(2025, 1, 1, 12, 0, 0),
        is_deleted=True,
    )
    doc = mr._task_to_doc(t)
    got = mr._doc_to_task(doc)
    assert got.id == t.id
    assert got.title == t.title
    assert got.description == t.description
    assert got.status == t.status
    assert got.priority == t.priority
    assert got.owner_id == t.owner_id
    assert got.assignee_id == t.assignee_id
    assert got.due_date == t.due_date
    assert getattr(got, "is_deleted", False) is True


def test_task_mapping_defaults_none():
    t = Task(id="t2", title="X", owner_id="u1")
    doc = mr._task_to_doc(t)
    got = mr._doc_to_task(doc)
    assert got.description == ""
    assert got.status == TaskStatus.NEW
    assert got.priority == Priority.NORMAL
    assert got.assignee_id is None
    assert got.due_date is None
    assert getattr(got, "is_deleted", False) is False


def test_event_mapping_roundtrip():
    e = TaskEvent(
        id="e1",
        task_id="t1",
        timestamp=datetime(2025, 1, 1, 12, 0, 0),
        type=EventType.CREATED,
        meta={"k": "v"},
    )
    doc = mr._event_to_doc(e)
    got = mr._doc_to_event(doc)
    assert got.id == e.id
    assert got.task_id == e.task_id
    assert got.timestamp == e.timestamp
    assert got.type == e.type
    assert got.meta == {"k": "v"}


def test_event_mapping_meta_default_empty():
    d = {
        "_id": "e2",
        "task_id": "t1",
        "timestamp": datetime(2025, 1, 1, 12, 0, 1),
        "type": "ASSIGNED",
    }
    got = mr._doc_to_event(d)
    assert got.meta == {}