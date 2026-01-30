import os
from flask import Flask, jsonify, request
from werkzeug.exceptions import NotFound

from src.serwis.task_service import TaskService
from src.repo.memory_repo import InMemoryUsers, InMemoryTasks, InMemoryEvents
from src.utils.idgen import IdGenerator
from src.utils.clock import Clock
from src.domain.user import User, Role, Status
from src.domain.task import Task
from src.domain.event import TaskEvent, EventType
from src.repo.memory_repo import InMemoryUsers, InMemoryTasks, InMemoryEvents

def _task_to_dict(t: Task) -> dict:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status.name,
        "priority": t.priority.name,
        "owner_id": t.owner_id,
        "assignee_id": t.assignee_id,
        "due_date": t.due_date.isoformat() if t.due_date else None,
        "is_deleted": bool(getattr(t, "is_deleted", False)),
    }

def _event_to_dict(e: TaskEvent) -> dict:
    return {
        "id": e.id,
        "task_id": e.task_id,
        "timestamp": e.timestamp.isoformat(),
        "type": e.type.name,
        "meta": e.meta,
    }

def _actor_id() -> str:
    aid = request.headers.get("X-Actor-Id")
    if not aid:
        raise ValueError("Missing X-Actor-Id header")
    return aid

def create_app() -> Flask:
    app = Flask(__name__)

    storage = os.getenv("STORAGE", "memory").lower()
    if storage == "mongo":
        from src.repo.mongo_repo import MongoUsers, MongoTasks, MongoEvents
        uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db  = os.getenv("MONGO_DB", "taskmgr")
        users, tasks, events = (
            MongoUsers(uri=uri, db_name=db),
            MongoTasks(uri=uri, db_name=db),
            MongoEvents(uri=uri, db_name=db),
        )
    else:
        users, tasks, events = InMemoryUsers(), InMemoryTasks(), InMemoryEvents()

    svc = TaskService(users, tasks, events, IdGenerator(), Clock())

    users.add(User(id="m1", email="m@example.com", role=Role.MANAGER, status=Status.ACTIVE,
                first_name="Manager", last_name="One", nickname="mm1"))
    users.add(User(id="u1", email="u1@example.com", role=Role.USER, status=Status.ACTIVE,
                first_name="User", last_name="One", nickname="uu1"))
    users.add(User(id="u2", email="u2@example.com", role=Role.USER, status=Status.ACTIVE,
                first_name="User", last_name="Two", nickname="uu2"))

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok"}, 200

    @app.errorhandler(ValueError)
    def _value_error(e: ValueError):
        return jsonify({"message": str(e)}), 400

    @app.errorhandler(PermissionError)
    def _perm_error(e: PermissionError):
        return jsonify({"message": str(e)}), 403

    @app.errorhandler(NotFound)
    def _not_found(e: NotFound):
        return jsonify({"message": "Not found"}), 404
    
    # nie testuje: 
    @app.errorhandler(Exception)
    def _unexpected(e: Exception):
        app.logger.exception("Unexpected error")
        return jsonify({"message": "Internal Server Error"}), 500

    # USERS
    @app.route("/api/users", methods=["POST"])
    def create_user():
        data = request.json
        required_fields = ["id", "email", "role", "status", "first_name", "last_name", "nickname"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing field: '{field}'"}), 400

        user = User(
            id=data["id"],
            email=data["email"],
            role=Role[data["role"]],
            status=Status[data["status"]],
            first_name=data["first_name"],
            last_name=data["last_name"],
            nickname=data["nickname"],
        )
        users.add(user)
        return jsonify({"id": user.id}), 201

    # TASKS
    @app.route("/api/tasks", methods=["POST"])
    def create_task():
        actor_id = _actor_id()
        data = request.get_json(force=True) or {}
        t = svc.create_task(
            actor_id,
            title=data.get("title", ""),
            description=data.get("description", ""),
            priority=data.get("priority", "NORMAL"),
        )
        return jsonify(_task_to_dict(t)), 201

    @app.route("/api/tasks/<task_id>", methods=["PATCH"])
    def update_task(task_id: str):
        actor_id = _actor_id()
        data = request.get_json(force=True) or {}
        t = svc.update_task(
            actor_id, task_id,
            title=data.get("title"),
            description=data.get("description"),
            priority=data.get("priority"),
        )
        return jsonify(_task_to_dict(t)), 200

    @app.route("/api/tasks/<task_id>/assign", methods=["POST"])
    def assign_task(task_id: str):
        actor_id = _actor_id()
        data = request.get_json(force=True) or {}
        assignee_id = data.get("assignee_id")
        if not assignee_id:
            raise ValueError("Missing assignee_id")
        t = svc.assign_task(actor_id, task_id, assignee_id)
        return jsonify(_task_to_dict(t)), 200

    @app.route("/api/tasks/<task_id>/status", methods=["POST"])
    def change_status(task_id: str):
        actor_id = _actor_id()
        data = request.get_json(force=True) or {}
        status = data.get("status")
        if not status:
            raise ValueError("Missing status")
        t = svc.change_status(actor_id, task_id, status)
        return jsonify(_task_to_dict(t)), 200

    @app.route("/api/tasks", methods=["GET"])
    def list_tasks():
        actor_id = _actor_id()
        items = svc.list_tasks(
            actor_id,
            status=request.args.get("status"),
            priority=request.args.get("priority"),
        )
        return jsonify([_task_to_dict(t) for t in items]), 200

    @app.route("/api/tasks/<task_id>", methods=["DELETE"])
    def delete_task(task_id: str):
        actor_id = _actor_id()
        t = svc.delete_task(actor_id, task_id)
        return jsonify(_task_to_dict(t)), 200

    @app.route("/api/tasks/<task_id>/events", methods=["GET"])
    def get_events(task_id: str):
        actor_id = _actor_id()
        evs = svc.get_events(actor_id, task_id)
        return jsonify([_event_to_dict(e) for e in evs]), 200
    
    @app.route("/api/tasks/<task_id>/email-history", methods=["POST"])
    def email_history(task_id: str):
        actor_id = _actor_id()
        data = request.get_json(force=True) or {}
        email = data.get("email")
        if not email:
            raise ValueError("Missing email")
        _ = svc.email_task_history(actor_id, task_id, email)
        return jsonify({"sent": True}), 200

    return app

if __name__ == "__main__":
    app = create_app()