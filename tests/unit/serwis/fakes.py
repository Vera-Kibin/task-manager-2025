from typing import Optional, List, Dict
from datetime import datetime, timedelta
from src.repo.interface import UsersRepository, TasksRepository, EventsRepository
from src.domain.user import User
from src.domain.task import Task
from src.domain.event import TaskEvent

class InMemoryUsers(UsersRepository):
    def __init__(self) -> None:
        self.items: Dict[str, User] = {}

    def get(self, user_id: str) -> Optional[User]:
        return self.items.get(user_id)

    def add(self, user: User) -> None:
        self.items[user.id] = user


class InMemoryTasks(TasksRepository):
    def __init__(self) -> None:
        self.items: Dict[str, Task] = {}

    def add(self, task: Task) -> None:
        self.items[task.id] = task

    def get(self, task_id: str) -> Optional[Task]:
        return self.items.get(task_id)

    def update(self, task: Task) -> None:
        self.items[task.id] = task

    def list(self) -> List[Task]:
        return list(self.items.values())


class InMemoryEvents(EventsRepository):
    def __init__(self) -> None:
        self.items: List[TaskEvent] = []

    def add(self, event: TaskEvent) -> None:
        self.items.append(event)

    def list_for_task(self, task_id: str) -> List[TaskEvent]:
        return sorted(
            (e for e in self.items if e.task_id == task_id),
            key=lambda e: e.timestamp,
        )


class FakeIdGen:
    def __init__(self) -> None:
        self._n = 0

    def new_id(self) -> str:
        self._n += 1
        return f"id-{self._n}"


class FakeClock:
    def __init__(self, start: Optional[datetime] = None) -> None:
        self._now = start or datetime(2025, 1, 1, 12, 0, 0)

    def now(self) -> datetime:
        t = self._now
        self._now = t + timedelta(seconds=1)
        return t