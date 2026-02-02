import os, uuid, requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
TIMEOUT = float(os.getenv("TEST_HTTP_TIMEOUT", "5.0"))

def new_email():
    return f"reg-{uuid.uuid4().hex[:8]}@ex.com"

def test_register_201_and_can_use_actor_id():
    r = requests.post(
        f"{BASE}/api/register",
        json={
            "email": new_email(),
            "first_name": "Alice",
            "last_name": "Wonderland",
            "nickname": "alice123",
        },
        timeout=TIMEOUT,
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body.get("message") == "User created"
    uid = body.get("id")
    assert isinstance(uid, str) and len(uid) > 0

    r2 = requests.post(
        f"{BASE}/api/tasks",
        headers={"Content-Type": "application/json", "X-Actor-Id": uid},
        json={"title": "Hello"},
        timeout=TIMEOUT,
    )
    assert r2.status_code == 201, r2.text
    assert r2.json()["title"] == "Hello"

def test_register_missing_field_400():
    r = requests.post(
        f"{BASE}/api/register",
        json={"email": new_email(), "first_name": "A"},
        timeout=TIMEOUT,
    )
    assert r.status_code == 400
    assert "Missing field" in r.json().get("message", "")

def test_register_bad_nickname_400():
    r = requests.post(
        f"{BASE}/api/register",
        json={
            "email": new_email(),
            "first_name": "Alice",
            "last_name": "Wonderland",
            "nickname": "x",
        },
        timeout=TIMEOUT,
    )
    assert r.status_code == 400
    assert "invalid nickname" in r.json().get("message", "").lower()