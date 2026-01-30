from dataclasses import dataclass
from enum import Enum, auto
import regex as re

class Role(Enum):
    USER = auto()
    MANAGER = auto()

class Status(Enum):
    ACTIVE = auto()
    BLOCKED = auto()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_NAME_RE = re.compile(r"^(?=.*\p{L})[\p{L}' -]{1,50}$")
_NICK_RE = re.compile(r"^[A-Za-z0-9_-]{3,32}$")

@dataclass
class User:
    id: str
    email: str
    role: Role
    status: Status
    first_name: str
    last_name: str
    nickname: str

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id.strip():
            raise ValueError("User.id must be non-empty")
        if not isinstance(self.role, Role):
            raise ValueError("role must be Role enum")
        if not isinstance(self.status, Status):
            raise ValueError("status must be Status enum")
        if not isinstance(self.email, str) or not _EMAIL_RE.match(self.email):
            raise ValueError("invalid email")
        if not isinstance(self.first_name, str) or not _NAME_RE.match(self.first_name):
            raise ValueError("invalid first_name")
        if not isinstance(self.last_name, str) or not _NAME_RE.match(self.last_name):
            raise ValueError("invalid last_name")
        if not isinstance(self.nickname, str) or not _NICK_RE.match(self.nickname):
            raise ValueError("invalid nickname")