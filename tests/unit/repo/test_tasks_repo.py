from src.repo.memory_repo import InMemoryTasks
from src.domain.task import Task, Priority, TaskStatus

def test_add_get_update_list_ok():
    repo = InMemoryTasks()
    t1 = Task(id="t1", title="A", owner_id="u1")
    t2 = Task(id="t2", title="B", owner_id="u2", priority=Priority.HIGH)

    repo.add(t1)
    repo.add(t2)

    # get
    assert repo.get("t1").title == "A"
    assert repo.get("t2").priority is Priority.HIGH
    assert repo.get("nope") is None

    # update
    t1.title = "A2"
    t1.status = TaskStatus.IN_PROGRESS
    repo.update(t1)
    got = repo.get("t1")
    assert got.title == "A2"
    assert got.status is TaskStatus.IN_PROGRESS

    # list
    all_ids = {t.id for t in repo.list()}
    assert all_ids == {"t1", "t2"}

def test_list_returns_copy_not_reference():
    repo = InMemoryTasks()
    repo.add(Task(id="t1", title="A", owner_id="u"))
    lst = repo.list()
    lst.clear()
    assert len(repo.list()) == 1