from datetime import datetime, timedelta
import types

from src.domain.user import User, Role, Status
from src.domain.task import Task, TaskStatus, Priority
from src.domain.event import TaskEvent, EventType
import src.repo.mongo_repo as mr


# --------- Fakes: kolekcja / kursor / klient ---------
class FakeCursor:
    def __init__(self, docs):
        self._docs = list(docs)

    def sort(self, spec):
        key = spec[0][0] if spec else None
        if key:
            self._docs = sorted(self._docs, key=lambda d: d.get(key))
        return self

    def __iter__(self):
        return iter(self._docs)


class FakeCollection:
    def __init__(self):
        self.docs = {}
        self.indexes = []

    def _match(self, d, flt):
        return all(d.get(k) == v for k, v in (flt or {}).items())

    def find_one(self, flt):
        for d in self.docs.values():
            if self._match(d, flt):
                return d.copy()
        return None

    def replace_one(self, flt, doc, upsert=False):
        if "_id" in flt:
            key = flt["_id"]
        elif "id" in flt:
            key = flt["id"]
        else:
            key = next(iter(flt.values()))
        self.docs[key] = doc.copy()
        return types.SimpleNamespace(matched_count=1, upserted_id=key if upsert else None)

    def insert_one(self, doc):
        key = doc.get("_id") or doc.get("id")
        self.docs[key] = doc.copy()
        return types.SimpleNamespace(inserted_id=key)

    def find(self, flt=None, projection=None):
        out = []
        for k, d in self.docs.items():
            if self._match(d, flt or {}):
                out.append(d.copy())
        return FakeCursor(out)

    def create_index(self, spec):
        self.indexes.append(spec)


class FakeDB:
    def __init__(self):
        self._cols = {}

    def __getitem__(self, name):
        if name not in self._cols:
            self._cols[name] = FakeCollection()
        return self._cols[name]


class FakeMongoClient:
    def __init__(self, uri):
        self._dbs = {}

    def __getitem__(self, db_name):
        if db_name not in self._dbs:
            self._dbs[db_name] = FakeDB()
        return self._dbs[db_name]


# --------- Tests: Users ---------
def test_mongo_users_get_add_with_injected_collection():
    col = FakeCollection()
    repo = mr.MongoUsers(collection=col)

    assert repo.get("u1") is None

    u = User(id="u1", email="u1@ex.com", role=Role.USER, status=Status.ACTIVE)
    repo.add(u)

    out = repo.get("u1")
    assert out and out.id == "u1" and out.role == Role.USER and out.status == Status.ACTIVE


def test_mongo_users_default_ctor_uses_client_and_env(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://example:27017")
    monkeypatch.setenv("MONGO_DB", "taskmgr")
    monkeypatch.setattr(mr, "MongoClient", FakeMongoClient)

    repo = mr.MongoUsers()
    u = User(id="ux", email="x@ex.com", role=Role.MANAGER, status=Status.ACTIVE)
    repo.add(u)
    assert repo.get("ux").role == Role.MANAGER


# --------- Tests: Tasks ---------
def _task(id_, owner, title="T", prio=Priority.NORMAL, status=TaskStatus.NEW):
    return Task(
        id=id_, title=title, description="",
        status=status, priority=prio,
        owner_id=owner, assignee_id=None, due_date=None, is_deleted=False
    )


def test_mongo_tasks_crud_with_injected_collection():
    col = FakeCollection()
    repo = mr.MongoTasks(collection=col)

    t = _task("t1", "u1")
    repo.add(t)
    got = repo.get("t1")
    assert got and got.id == "t1" and got.status == TaskStatus.NEW
    t.assignee_id = "dev1"
    t.priority = Priority.HIGH
    t.due_date = datetime(2025, 1, 1, 12, 0, 0)
    repo.update(t)

    got2 = repo.get("t1")
    assert got2.assignee_id == "dev1"
    assert got2.priority == Priority.HIGH
    assert got2.due_date == datetime(2025, 1, 1, 12, 0, 0)

    repo.add(_task("t2", "u1", title="X"))
    all_tasks = repo.list()
    assert {x.id for x in all_tasks} == {"t1", "t2"}


def test_mongo_tasks_default_ctor_and_list(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://x")
    monkeypatch.setenv("MONGO_DB", "taskmgr")
    monkeypatch.setattr(mr, "MongoClient", FakeMongoClient)

    repo = mr.MongoTasks()
    repo.add(_task("a", "u"))
    repo.add(_task("b", "u"))
    assert {t.id for t in repo.list()} == {"a", "b"}


# --------- Tests: Events ---------
def test_mongo_events_add_and_sorted_listing_injected_col():
    col = FakeCollection()
    repo = mr.MongoEvents(collection=col)

    tid_a, tid_b = "ta", "tb"
    t0 = datetime(2025, 1, 1, 12, 0, 0)
    e2 = TaskEvent("e2", tid_a, t0 + timedelta(seconds=1), EventType.ASSIGNED, {})
    e1 = TaskEvent("e1", tid_a, t0, EventType.CREATED, {})
    x1 = TaskEvent("x1", tid_b, t0 + timedelta(seconds=2), EventType.UPDATED, {})

    repo.add(e2)
    repo.add(e1)
    repo.add(x1)

    out = repo.list_for_task(tid_a)
    assert [e.id for e in out] == ["e1", "e2"]


def test_mongo_events_default_ctor_creates_index(monkeypatch):
    monkeypatch.setenv("MONGO_URI", "mongodb://x")
    monkeypatch.setenv("MONGO_DB", "taskmgr")
    monkeypatch.setattr(mr, "MongoClient", FakeMongoClient)
    repo = mr.MongoEvents()
    idx = repo._collection.indexes[0]
    assert [k for (k, _v) in idx] == ["task_id", "timestamp"]