from datetime import datetime
from src.serwis.task_service import TaskService
from .fakes import InMemoryUsers, InMemoryTasks, InMemoryEvents, FakeIdGen, FakeClock

def make_service():
    users, tasks, events = InMemoryUsers(), InMemoryTasks(), InMemoryEvents()
    idgen = FakeIdGen()
    clock = FakeClock(datetime(2025, 1, 1, 12, 0, 0))
    return TaskService(users, tasks, events, idgen, clock), users, tasks, events