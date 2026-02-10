from __future__ import annotations

"""
Completion record model.

Represents a single completion event for a habit. The DB may contain multiple 
completion rows, but the application logic prevents more than one completion 
per habit per period.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Completion:
    id: int | None
    habit_id: int
    completed_at: datetime
