"""Staff accounts and their open sessions, in memory until the database arrives."""

from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, List, Optional, Tuple

from app.data.sample_data import SAMPLE_USERS
from app.schemas import User, UserCreate
from app.security import hash_password, new_token, verify_password

SESSION_DURATION = timedelta(hours=12)

# Hashing is slow on purpose, so the demo users are hashed once and reused on reset.
_SAMPLE_ACCOUNTS: List[Tuple[User, str]] = [
    (User(id=index, username=username, full_name=full_name, role=role), hash_password(password))
    for index, (username, full_name, role, password) in enumerate(SAMPLE_USERS, start=1)
]


class UserStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._users: Dict[int, User] = {}
        self._password_hashes: Dict[int, str] = {}
        self._sessions: Dict[str, Tuple[int, datetime]] = {}
        self._next_id = 1
        self.reset()

    def reset(self) -> None:
        with self._lock:
            self._users = {user.id: user for user, _ in _SAMPLE_ACCOUNTS}
            self._password_hashes = {user.id: password_hash for user, password_hash in _SAMPLE_ACCOUNTS}
            self._sessions = {}
            self._next_id = max(self._users, default=0) + 1

    # Accounts

    def list(self) -> List[User]:
        with self._lock:
            return sorted(self._users.values(), key=lambda user: (user.role != "manager", user.full_name))

    def get(self, user_id: int) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)

    def username_taken(self, username: str) -> bool:
        with self._lock:
            return any(user.username == username for user in self._users.values())

    def count_role(self, role: str) -> int:
        with self._lock:
            return sum(1 for user in self._users.values() if user.role == role)

    def add(self, data: UserCreate) -> User:
        password_hash = hash_password(data.password)  # outside the lock: it is slow
        with self._lock:
            user = User(id=self._next_id, username=data.username, full_name=data.full_name, role=data.role)
            self._users[user.id] = user
            self._password_hashes[user.id] = password_hash
            self._next_id += 1
            return user

    def delete(self, user_id: int) -> None:
        with self._lock:
            self._users.pop(user_id, None)
            self._password_hashes.pop(user_id, None)
            # A deleted account cannot keep using a token it already had.
            self._sessions = {token: s for token, s in self._sessions.items() if s[0] != user_id}

    # Sessions

    def authenticate(self, username: str, password: str) -> Optional[User]:
        with self._lock:
            user = next((u for u in self._users.values() if u.username == username), None)
            password_hash = self._password_hashes.get(user.id) if user else None
        if user is None or password_hash is None or not verify_password(password, password_hash):
            return None
        return user

    def open_session(self, user_id: int) -> str:
        token = new_token()
        with self._lock:
            self._sessions[token] = (user_id, datetime.now() + SESSION_DURATION)
        return token

    def user_for_token(self, token: str) -> Optional[User]:
        with self._lock:
            session = self._sessions.get(token)
            if session is None:
                return None
            user_id, expires_at = session
            if expires_at < datetime.now():
                del self._sessions[token]
                return None
            return self._users.get(user_id)

    def close_session(self, token: str) -> None:
        with self._lock:
            self._sessions.pop(token, None)


user_store = UserStore()
