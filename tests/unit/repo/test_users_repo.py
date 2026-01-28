from src.repo.memory_repo import InMemoryUsers
from src.domain.user import User, Role, Status

def test_add_and_get_user_ok():
    repo = InMemoryUsers()
    u = User(id="u1", email="u1@ex.com", role=Role.USER, status=Status.ACTIVE)
    repo.add(u)
    got = repo.get("u1")
    assert got is not None
    assert got.email == "u1@ex.com"

def test_get_unknown_returns_none():
    repo = InMemoryUsers()
    assert repo.get("ghost") is None