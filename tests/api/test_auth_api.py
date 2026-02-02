import os, uuid, requests
BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")
TIMEOUT = float(os.getenv("TEST_HTTP_TIMEOUT", "5.0"))

def nid(p): return f"{p}-{uuid.uuid4().hex[:8]}"

def test_register_201_and_can_use_api():
    # rejestracja
    email = f"{nid('u')}@ex.com"
    r = requests.post(f"{BASE}/api/register", json={
        "first_name": "Vera", "last_name": "Kibin", "nickname": "vera_k",
        "email": email,
    }, timeout=TIMEOUT)
    assert r.status_code == 201, r.text
    uid = r.json()["id"]

    r2 = requests.post(f"{BASE}/api/tasks",
        headers={"X-Actor-Id": uid, "Content-Type": "application/json"},
        json={"title": "Hello"}, timeout=TIMEOUT)
    assert r2.status_code == 201, r2.text
    assert r2.json()["title"] == "Hello"

def test_register_missing_field_400():
    r = requests.post(f"{BASE}/api/register", json={
        "first_name": "A", "last_name": "B", "nickname": "ab"
    }, timeout=TIMEOUT)
    assert r.status_code == 400
    assert "Missing field" in r.json().get("message","")

def test_login_ok():
    email = f"{nid('u')}@ex.com"
    rr = requests.post(f"{BASE}/api/register", json={
        "first_name": "John", "last_name": "Doe", "nickname": "john_d", "email": email
    }, timeout=TIMEOUT)
    assert rr.status_code == 201
    r = requests.post(f"{BASE}/api/login", json={
        "email": email, "nickname": "john_d"
    }, timeout=TIMEOUT)
    assert r.status_code == 200
    body = r.json()
    assert "id" in body and body["nickname"] == "john_d"

def test_login_404_user_not_found():
    r = requests.post(f"{BASE}/api/login", json={
        "email": f"{nid('x')}@ex.com", "nickname": "nope"
    }, timeout=TIMEOUT)
    assert r.status_code == 404
    assert "User not found" in r.json().get("message","")