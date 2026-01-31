import os
import uuid
import requests
import random
import pytest

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
PERF_LIMIT = float(os.getenv("PERF_LIMIT", "0.5")) # maksymalny czas jednego requestu
PERF_N = int(os.getenv("PERF_N", "60")) # liczba iteracji

def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def H(actor_id: str) -> dict:
    return {"Content-Type": "application/json", "X-Actor-Id": actor_id}

def _assert_fast(resp: requests.Response, label: str):
    took = resp.elapsed.total_seconds()
    assert took < PERF_LIMIT, f"{label} took {took:.3f}s >= {PERF_LIMIT}s"

def _create_user(user_id: str, role="USER", status="ACTIVE", first_name="John", last_name="Doe", nickname="john_doe"):
    r = requests.post(f"{BASE}/api/users",json={"id": user_id, "email": f"{user_id}@ex.com", "role": role, "status": status, "first_name": first_name, "last_name": last_name, "nickname": nickname},timeout=5)
    assert r.status_code in (200, 201), r.text
    _assert_fast(r, f"create user {user_id}")

def _create_task(actor_id: str, title: str):
    r = requests.post(f"{BASE}/api/tasks", headers=H(actor_id), json={"title": title}, timeout=5)
    assert r.status_code == 201, r.text
    _assert_fast(r, f"create task {title}")
    return r.json()["id"]

def _list_tasks(actor_id: str):
    r = requests.get(f"{BASE}/api/tasks", headers=H(actor_id), timeout=5)
    assert r.status_code == 200
    _assert_fast(r, "list tasks")
    return r.json()

def _delete_task(actor_id: str, task_id: str):
    r = requests.delete(f"{BASE}/api/tasks/{task_id}", headers=H(actor_id), timeout=5)
    assert r.status_code == 200
    _assert_fast(r, f"delete {task_id}")

def _assign(actor_id: str, task_id: str, assignee: str):
    r = requests.post(f"{BASE}/api/tasks/{task_id}/assign", headers=H(actor_id),
                      json={"assignee_id": assignee}, timeout=5)
    assert r.status_code == 200, r.text
    _assert_fast(r, f"assign {task_id}")

def _status(actor_id: str, task_id: str, status: str):
    r = requests.post(f"{BASE}/api/tasks/{task_id}/status", headers=H(actor_id),
                      json={"status": status}, timeout=5)
    assert r.status_code == 200, r.text
    _assert_fast(r, f"status {task_id} -> {status}")

@pytest.fixture(scope="module")
def s():
    with requests.Session() as sess:
        yield sess

def test_perf_create_list_delete_many_tasks(s):
    owner = _new_id("owner")
    _create_user(owner, role="USER")

    for t in _list_tasks(owner):
        _delete_task(owner, t["id"])

    task_ids = []
    for i in range(PERF_N):
        title = f"T-{i}-{random.randint(0, 9999)}"
        task_ids.append(_create_task(owner, title))

    items = _list_tasks(owner)
    ids = {t["id"] for t in items}
    assert set(task_ids).issubset(ids)

    for tid in task_ids:
        _delete_task(owner, tid)

    assert len(_list_tasks(owner)) == 0

def test_perf_assign_and_status_flow(s):
    mgr = _new_id("mgr"); dev = _new_id("dev")
    _create_user(mgr, role="MANAGER")
    _create_user(dev, role="USER")
    # create -> assign -> IN_PROGRESS -> DONE
    for i in range(PERF_N):
        tid = _create_task(mgr, f"F-{i}")
        _assign(mgr, tid, dev)
        _status(dev, tid, "IN_PROGRESS")
        _status(dev, tid, "DONE")