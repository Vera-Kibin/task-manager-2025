from behave import given, when, then, step
import os
import uuid
import requests

BASE = os.getenv("BASE_URL", "http://127.0.0.1:5000")

def H(actor_id: str) -> dict:
    return {"Content-Type": "application/json", "X-Actor-Id": actor_id}

def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

# -------- helpers: API --------
def _create_user(user_id: str, role: str = "USER", status: str = "ACTIVE", first_name: str = "John", last_name: str = "Doe", nickname: str = "john_doe"):
    r = requests.post(
        f"{BASE}/api/users",
        json={"id": user_id, "email": f"{user_id}@ex.com", "role": role, "status": status, "first_name": first_name, "last_name": last_name, "nickname": nickname},
        timeout=5,
    )
    assert r.status_code == 201, r.text

def _create_task(actor: str, title: str):
    r = requests.post(f"{BASE}/api/tasks", headers=H(actor), json={"title": title}, timeout=5)
    return r

def _list_tasks(actor: str):
    return requests.get(f"{BASE}/api/tasks", headers=H(actor), timeout=5)

def _delete_task(actor: str, task_id: str):
    return requests.delete(f"{BASE}/api/tasks/{task_id}", headers=H(actor), timeout=5)

def _patch_task(actor: str, task_id: str, payload: dict):
    return requests.patch(f"{BASE}/api/tasks/{task_id}", headers=H(actor), json=payload, timeout=5)

def _assign(actor: str, task_id: str, assignee: str):
    return requests.post(
        f"{BASE}/api/tasks/{task_id}/assign",
        headers=H(actor),
        json={"assignee_id": assignee},
        timeout=5,
    )

def _status(actor: str, task_id: str, status: str):
    return requests.post(
        f"{BASE}/api/tasks/{task_id}/status",
        headers=H(actor),
        json={"status": status},
        timeout=5,
    )

def _events(actor: str, task_id: str):
    return requests.get(f"{BASE}/api/tasks/{task_id}/events", headers=H(actor), timeout=5)

# -------- generic steps --------
@when('I GET "/health"')
def step_health_get(context):
    context.last_response = requests.get(f"{BASE}/health", timeout=5)

@then('Response status is "{code}"')
def step_resp_status_is(context, code):
    assert context.last_response.status_code == int(code)

@then('Response JSON has key "{key}" with value "{value}"')
def step_resp_json_key_value(context, key, value):
    body = context.last_response.json()
    assert body.get(key) == value

# -------- users / setup --------
@given('User "{user_id}" with role "{role}" exists')
def step_user_exists(context, user_id, role):
    _create_user(user_id, role=role)

@given('Task list for actor "{actor}" is empty')
def step_clean_for_actor(context, actor):
    r = _list_tasks(actor)
    if r.status_code == 200:
        for t in r.json():
            _delete_task(actor, t["id"])

# -------- tasks: create / list --------
@when('Actor "{actor}" creates a task titled "{title}"')
def step_create_task(context, actor, title):
    r = _create_task(actor, title)
    assert r.status_code == 201, r.text
    context.last_response = r
    context.task_id = r.json()["id"]

@then('Actor "{actor}" sees last task in list')
def step_owner_sees(context, actor):
    r = _list_tasks(actor)
    assert r.status_code == 200
    ids = {t["id"] for t in r.json()}
    assert context.task_id in ids

@then('Actor "{actor}" does not see last task in list')
def step_other_not_see(context, actor):
    r = _list_tasks(actor)
    assert r.status_code == 200
    ids = {t["id"] for t in r.json()}
    assert context.task_id not in ids

# -------- update / delete --------
@when('Actor "{actor}" updates the task title to "{title}" and priority to "{prio}"')
def step_update_task(context, actor, title, prio):
    r = _patch_task(actor, context.task_id, {"title": title, "priority": prio})
    context.last_response = r

@when('Actor "{actor}" deletes the task')
def step_delete_task(context, actor):
    r = _delete_task(actor, context.task_id)
    context.last_response = r
    assert r.status_code == 200

@then('Task is hidden from list for actor "{actor}"')
def step_hidden_from_list(context, actor):
    r = _list_tasks(actor)
    assert r.status_code == 200
    assert context.task_id not in {t["id"] for t in r.json()}

@then('Last response status is "{code}"')
def step_last_status(context, code):
    assert context.last_response.status_code == int(code)

@then('Last response JSON has key "{key}" with value "{value}"')
def step_last_json_key_value(context, key, value):
    assert context.last_response.json().get(key) == value

@then('Last response JSON message contains "{frag}"')
def step_last_json_msg_contains(context, frag):
    assert frag in context.last_response.json().get("message", "")

# -------- assign / status / events --------
@when('Actor "{actor}" assigns the task to "{assignee}"')
def step_assign_ok(context, actor, assignee):
    r = _assign(actor, context.task_id, assignee)
    context.last_response = r
    assert r.status_code == 200

@when('Actor "{actor}" tries to assign the task to "{assignee}"')
def step_assign_try(context, actor, assignee):
    context.last_response = _assign(actor, context.task_id, assignee)

@when('Actor "{actor}" changes status to "{status}"')
def step_change_status_ok(context, actor, status):
    r = _status(actor, context.task_id, status)
    context.last_response = r
    assert r.status_code == 200

@when('Actor "{actor}" tries to change status to "{status}"')
def step_change_status_try(context, actor, status):
    context.last_response = _status(actor, context.task_id, status)

@then('Events for the task seen by "{actor}" include "{etype}"')
def step_events_include(context, actor, etype):
    r = _events(actor, context.task_id)
    assert r.status_code == 200
    kinds = [e["type"] for e in r.json()]
    assert etype in kinds

@then('Events for the task seen by "{actor}" contain "{etype}" exactly "{count}" times')
def step_events_count(context, actor, etype, count):
    r = _events(actor, context.task_id)
    assert r.status_code == 200
    kinds = [e["type"] for e in r.json()]
    assert kinds.count(etype) == int(count)