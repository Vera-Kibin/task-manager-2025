import pytest
from src.serwis.task_service import TaskService
from src.repo.memory_repo import InMemoryUsers, InMemoryTasks, InMemoryEvents
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock
from src.domain.user import User, Role, Status

@pytest.fixture
def repos():
    return InMemoryUsers(), InMemoryTasks(), InMemoryEvents()

@pytest.fixture
def svc(repos):
    users, tasks, events = repos
    return TaskService(users, tasks, events, IdGenerator(), Clock())

@pytest.fixture
def owner(repos):
    users, *_ = repos
    users.add(User(id="owner-1", email="o@ex.com", role=Role.USER, status=Status.ACTIVE, first_name="Owner", last_name="One", nickname="owner_o"))
    return "owner-1"

@pytest.fixture
def owner_with_task(svc, owner, mocker):
    mocker.patch("src.utils.idgen.IdGenerator.new_id", return_value="t-fixed")
    t = svc.create_task(actor_id=owner, title="T", description="", priority="NORMAL")
    return owner, t.id

def test_email_history_calls_smtp(mocker, svc, owner_with_task):
    actor_id, task_id = owner_with_task
    mock_send = mocker.patch("src.integrations.emailer.SMTPClient.send", return_value=True)
    ok = svc.email_task_history(actor_id, task_id, "a@b.c")
    assert ok is True
    mock_send.assert_called_once()
    subject, body, to_ = mock_send.call_args[0]
    assert "Task History" in subject and to_ == "a@b.c"

def test_email_history_missing_email_raises(svc, owner_with_task):
    actor_id, task_id = owner_with_task
    with pytest.raises(ValueError, match="Missing email"):
        svc.email_task_history(actor_id, task_id, "")

def test_email_history_raises_notfound_when_task_missing(mocker, svc, owner):
    mocker.patch.object(svc, "get_events", return_value=[])
    mocker.patch.object(svc.tasks, "get", return_value=None)
    from werkzeug.exceptions import NotFound
    with pytest.raises(NotFound):
        svc.email_task_history(owner, "no-such-id", "a@b.c")