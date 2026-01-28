from datetime import datetime
from src.repo.memory_repo import InMemoryEvents
from src.domain.event import TaskEvent, EventType

def test_list_for_task_filters_and_sorts_by_timestamp():
    repo = InMemoryEvents()
    tid_a = "ta"
    tid_b = "tb"

    repo.add(TaskEvent("e2", tid_a, datetime(2025,1,1,12,0,1), EventType.ASSIGNED, {}))
    repo.add(TaskEvent("e1", tid_a, datetime(2025,1,1,12,0,0), EventType.CREATED, {}))
    repo.add(TaskEvent("x1", tid_b, datetime(2025,1,1,12,0,2), EventType.UPDATED, {}))

    out = repo.list_for_task(tid_a)
    assert [e.id for e in out] == ["e1", "e2"]
    assert all(e.task_id == tid_a for e in out)

def test_list_for_task_empty_for_unknown_task():
    repo = InMemoryEvents()
    assert repo.list_for_task("nope") == []