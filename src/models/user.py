"""
User domain model.

Encapsulates the minimal user information used by the application.
The project historically supported a single default user; the model
is included to keep the domain explicit and to make future
multi-user migration straightforward.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: int
    username: str
    created_at: datetime
