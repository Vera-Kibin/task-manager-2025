from datetime import datetime
from pytest_mock import MockerFixture

from src.serwis.task_service import TaskService
from src.repo.memory_repo import InMemoryUsers, InMemoryTasks, InMemoryEvents
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock
from src.domain.user import User, Role, Status
from src.domain.task import TaskStatus

def _svc():
    users = InMemoryUsers()
    tasks = InMemoryTasks()
    events = InMemoryEvents()
    return users, tasks, events

def test_create_task_uses_mocked_id_and_clock(mocker: MockerFixture):
    users, tasks, events = _svc()
    users.add(User(id="u1", email="u1@ex.com", role=Role.USER, status=Status.ACTIVE, first_name="John", last_name="Doe", nickname="john_doe"))

    mocker.patch("src.utils.idgen.IdGenerator.new_id", return_value="fixed-id-123")
    fixed_now = datetime(2025, 1, 1, 12, 0, 0)
    mocker.patch("src.utils.clock.Clock.now", return_value=fixed_now)

    svc = TaskService(users, tasks, events, IdGenerator(), Clock())

    t = svc.create_task(actor_id="u1", title="Hello", description="", priority="NORMAL")

    assert t.id == "fixed-id-123"
    assert t.status == TaskStatus.NEW
    evs = events.list_for_task(t.id)
    assert any(e.type.name == "CREATED" and e.timestamp == fixed_now for e in evs)

def test_status_change_event_uses_mocked_clock(mocker: MockerFixture):
    users, tasks, events = _svc()
    users.add(User(id="u1", email="u1@ex.com", role=Role.USER, status=Status.ACTIVE, first_name="John", last_name="Doe", nickname="john_doe"))

    mocker.patch("src.utils.idgen.IdGenerator.new_id", return_value="tid-1")
    mocker.patch("src.utils.clock.Clock.now", return_value=datetime(2025, 1, 1, 12, 0, 0))

    svc = TaskService(users, tasks, events, IdGenerator(), Clock())
    t = svc.create_task("u1", "X", "", "NORMAL")

    later = datetime(2025, 1, 1, 12, 5, 0)
    mocker.patch("src.utils.clock.Clock.now", return_value=later)

    svc.change_status("u1", t.id, "IN_PROGRESS")

    evs = events.list_for_task(t.id)
    ts_for_status = [e.timestamp for e in evs if e.type.name == "STATUS_CHANGED"]
    assert ts_for_status and ts_for_status[-1] == later