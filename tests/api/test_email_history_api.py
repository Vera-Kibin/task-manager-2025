import os
import uuid
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
TIMEOUT = float(os.getenv("TEST_HTTP_TIMEOUT", "5.0"))

def H(actor_id: str) -> dict:
    return {"Content-Type": "application/json", "X-Actor-Id": actor_id}

def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def create_user(user_id: str, role: str = "USER", status: str = "ACTIVE", first_name: str = "John", last_name: str = "Doe", nickname: str = "john_doe") -> None:
    r = requests.post(
        f"{BASE}/api/users",
        json={"id": user_id, "email": f"{user_id}@ex.com", "role": role, "status": status, "first_name": first_name, "last_name": last_name, "nickname": nickname},
        timeout=TIMEOUT,
    )
    assert r.status_code == 201, r.text

def create_task(actor_id: str, title: str = "T") -> dict:
    r = requests.post(f"{BASE}/api/tasks", headers=H(actor_id), json={"title": title}, timeout=TIMEOUT)
    assert r.status_code == 201, r.text
    return r.json()

def test_email_history_happy_path_returns_sent_true():
    owner = new_id("owner")
    create_user(owner)

    t = create_task(owner, "Feature-X")

    r = requests.post(
        f"{BASE}/api/tasks/{t['id']}/email-history",
        headers=H(owner),
        json={"email": "a@b.c"},
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json() == {"sent": True}