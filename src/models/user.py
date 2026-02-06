from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    """
    Represents the owner of habits.

    The application currently supports a single user.
    This class exists to keep the domain model clean
    and allow future multi-user extensions.
    """
    id: int
    username: str
    created_at: datetime
