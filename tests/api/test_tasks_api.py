import os
import uuid
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
TIMEOUT = float(os.getenv("TEST_HTTP_TIMEOUT", "5.0"))

def H(actor_id: str) -> dict:
    return {"Content-Type": "application/json", "X-Actor-Id": actor_id}


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def create_user(user_id: str, role: str = "USER", status: str = "ACTIVE", first_name: str = "John", last_name: str = "Doe", nickname: str = None) -> None:
    if nickname is None:
        nickname = f"nick_{user_id[:6]}"
    r = requests.post(
        f"{BASE}/api/users",
        json={"id": user_id, "email": f"{user_id}@ex.com", "role": role, "status": status, "first_name": first_name, "last_name": last_name, "nickname": nickname},timeout=TIMEOUT,
    )
    assert r.status_code == 201, r.text


def create_task(actor_id: str, title: str = "T") -> dict:
    r = requests.post(f"{BASE}/api/tasks", headers=H(actor_id), json={"title": title}, timeout=TIMEOUT,)
    assert r.status_code == 201, r.text
    return r.json()


# ---------------------- sanity / health ----------------------

def test_health():
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_create_user_201():
    u = new_id("api-u")
    r = requests.post(
        f"{BASE}/api/users",
        json={"id": u, "email": f"{u}@ex.com", "role": "USER", "status": "ACTIVE", "first_name": "John", "last_name": "Doe", "nickname": "john_doe"},
    )
    assert r.status_code == 201
    assert r.json()["message"] == "User created"

def test_create_user_missing_field_400():
    r = requests.post(f"{BASE}/api/users", json={"email": "x@ex.com"})
    assert r.status_code == 400
    assert "Missing field" in r.json().get("message", "")

# ---------------------- CRUD: create/list/update/delete ----------------------

def test_create_and_list_tasks_visible_for_owner_only():
    owner = new_id("owner")
    other = new_id("other")
    create_user(owner)
    create_user(other)

    t1 = create_task(owner, "Task-A")
    _ = create_task(owner, "Task-B")

    r = requests.get(f"{BASE}/api/tasks", headers=H(owner))
    assert r.status_code == 200
    ids = {t["id"] for t in r.json()}
    assert t1["id"] in ids

    # inny user nie widzi
    r2 = requests.get(f"{BASE}/api/tasks", headers=H(other))
    assert r2.status_code == 200
    ids2 = {t["id"] for t in r2.json()}
    assert t1["id"] not in ids2

def test_create_task_unknown_priority_400():
    u = new_id("u")
    create_user(u)
    r = requests.post(
        f"{BASE}/api/tasks",
        headers=H(u),
        json={"title": "X", "priority": "ULTRA"},
    )
    assert r.status_code == 400
    assert "Unknown priority" in r.json().get("message", "")

def test_update_then_delete_hides_from_list():
    owner = new_id("owner")
    create_user(owner)
    t = create_task(owner, "Old")

    r = requests.patch(
        f"{BASE}/api/tasks/{t['id']}",
        headers=H(owner),
        json={"title": "New", "priority": "HIGH"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "New"
    assert body["priority"] == "HIGH"

    r2 = requests.delete(f"{BASE}/api/tasks/{t['id']}", headers=H(owner))
    assert r2.status_code == 200
    assert r2.json()["is_deleted"] is True

    r3 = requests.get(f"{BASE}/api/tasks", headers=H(owner))
    assert r3.status_code == 200
    assert t["id"] not in {x["id"] for x in r3.json()}

def test_update_invalid_title_400():
    u = new_id("u")
    create_user(u)
    t = create_task(u, "Ok")
    r = requests.patch(
        f"{BASE}/api/tasks/{t['id']}",
        headers=H(u),
        json={"title": ""},
    )
    assert r.status_code == 400
    assert "Invalid title" in r.json().get("message", "")

def test_update_unknown_priority_400():
    u = new_id("u")
    create_user(u)
    t = create_task(u, "Ok")
    r = requests.patch(
        f"{BASE}/api/tasks/{t['id']}",
        headers=H(u),
        json={"priority": "NOPE"},
    )
    assert r.status_code == 400
    assert "Unknown priority" in r.json().get("message", "")

def test_update_missing_actor_header_400():
    u = new_id("u")
    create_user(u)
    t = create_task(u, "Ok")
    r = requests.patch(
        f"{BASE}/api/tasks/{t['id']}",
        json={"title": "New"},
    )
    assert r.status_code == 400
    assert "Missing X-Actor-Id" in r.json().get("message", "")


# ---------------------- assign / status / events ----------------------

def test_assign_and_events_flow():
    mgr = new_id("mgr")
    dev = new_id("dev")
    create_user(mgr, role="MANAGER")
    create_user(dev, role="USER")

    t = create_task(mgr, "Feature-1")

    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/assign",
        headers=H(mgr),
        json={"assignee_id": dev},
    )
    assert r.status_code == 200
    assert r.json()["assignee_id"] == dev

    r2 = requests.get(f"{BASE}/api/tasks/{t['id']}/events", headers=H(mgr))
    assert r2.status_code == 200
    kinds = [e["type"] for e in r2.json()]
    assert "ASSIGNED" in kinds

def test_assign_missing_assignee_id_400():
    m = new_id("m"); create_user(m, role="MANAGER")
    t = create_task(m, "A")
    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/assign",
        headers=H(m),
        json={},
    )
    assert r.status_code == 400
    assert "Missing assignee_id" in r.json().get("message", "")

def test_status_happy_path_and_events():
    owner = new_id("owner")
    dev = new_id("dev")
    create_user(owner)
    create_user(dev)

    t = create_task(owner, "Impl")
   
    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/assign",
        headers=H(owner),
        json={"assignee_id": dev},
    )
    assert r.status_code == 200
    # IN_PROGRESS -> DONE
    r1 = requests.post(
        f"{BASE}/api/tasks/{t['id']}/status",
        headers=H(dev),
        json={"status": "IN_PROGRESS"},
    )
    assert r1.status_code == 200

    r2 = requests.post(
        f"{BASE}/api/tasks/{t['id']}/status",
        headers=H(dev),
        json={"status": "DONE"},
    )
    assert r2.status_code == 200

    r3 = requests.get(f"{BASE}/api/tasks/{t['id']}/events", headers=H(dev))
    assert r3.status_code == 200
    kinds = [e["type"] for e in r3.json()]
    assert kinds.count("STATUS_CHANGED") == 2

def test_status_illegal_transition_400():
    u = new_id("u"); create_user(u)
    t = create_task(u, "A")
    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/status",
        headers=H(u),
        json={"status": "DONE"},
    )
    assert r.status_code == 400
    assert "Invalid status transition" in r.json().get("message", "")

def test_status_missing_field_400():
    u = new_id("u"); create_user(u)
    t = create_task(u, "A")
    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/status",
        headers=H(u),
        json={},
    )
    assert r.status_code == 400
    assert "Missing status" in r.json().get("message", "")

# --- LIST (filtry) ---

def test_list_filters_by_status_and_priority():
    u = new_id("u"); create_user(u)
    t1 = create_task(u, "T1")  # NORMAL/NEW
    t2 = create_task(u, "T2")  # bedzie HIGH/IN_PROGRESS

    r_upd = requests.patch(
        f"{BASE}/api/tasks/{t2['id']}",
        headers=H(u),
        json={"priority": "HIGH"},
    )
    assert r_upd.status_code == 200
    r_st = requests.post(
        f"{BASE}/api/tasks/{t2['id']}/status",
        headers=H(u),
        json={"status": "IN_PROGRESS"},
    )
    assert r_st.status_code == 200

    r_s = requests.get(f"{BASE}/api/tasks?status=IN_PROGRESS", headers=H(u))
    assert r_s.status_code == 200
    assert {x["id"] for x in r_s.json()} == {t2["id"]}

    r_p = requests.get(f"{BASE}/api/tasks?priority=HIGH", headers=H(u))
    assert r_p.status_code == 200
    assert {x["id"] for x in r_p.json()} == {t2["id"]}

# --- DELETE ---

def test_delete_only_owner_gets_403():
    owner = new_id("o"); other = new_id("x")
    create_user(owner); create_user(other)
    t = create_task(owner, "Secret")
    r = requests.delete(f"{BASE}/api/tasks/{t['id']}", headers=H(other))
    assert r.status_code == 403
    assert "Only owner can delete" in r.json().get("message", "")

# --- EVENTS / uprawnienia ---

def test_events_forbidden_for_unrelated_actor_403():
    owner = new_id("o"); stranger = new_id("x")
    create_user(owner); create_user(stranger)
    t = create_task(owner, "Sec")
    r = requests.get(f"{BASE}/api/tasks/{t['id']}/events", headers=H(stranger))
    assert r.status_code == 403

# ---------------------- walidacja / blędy ----------------------

def test_missing_actor_header_returns_400():
    r = requests.post(f"{BASE}/api/tasks", json={"title": "X"})
    assert r.status_code == 400
    assert "Missing X-Actor-Id header" in r.json().get("message", "")


def test_unknown_status_returns_400():
    u = new_id("u")
    create_user(u)
    t = create_task(u, "X")
    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/status",
        headers=H(u),
        json={"status": "WHAT_IS_THIS"},
    )
    assert r.status_code == 400
    assert "Unknown status" in r.json().get("message", "")


def test_forbidden_assign_returns_403():
    owner = new_id("o")
    other = new_id("x")
    target = new_id("a")
    create_user(owner)
    create_user(other)
    create_user(target)

    t = create_task(owner, "Secret")
    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/assign",
        headers=H(other),
        json={"assignee_id": target},
    )
    assert r.status_code == 403
    assert "User cannot assign this task" in r.json().get("message", "")

def test_404_unknown_route():
    r = requests.get(f"{BASE}/api/no-such-route", headers=H(new_id("u")))
    assert r.status_code == 404
    assert r.json().get("message") == "Not found"