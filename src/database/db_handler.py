from __future__ import annotations

"""
Persistence layer (SQLite) for the Habit Tracker.

Why this file exists and design notes:
- Uses a lightweight file-backed SQLite DB to keep the project
    simple and dependency-free for a small single-user CLI tool.
- Dates are stored as formatted strings (`DT_FMT`) for portability
    and ease of reading when inspecting the DB file manually.
- Foreign key cascades are enabled so deleting users/habits
    automatically removes dependent rows (habits -> completions).
- The handler intentionally provides simple, explicit methods
    mapping closely to application operations (create/list/get/delete).
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from src.models.habit import Habit, Periodicity
from src.models.completion import Completion
from src.models.user import User

# Consistent format used when persisting datetimes to SQLite TEXT columns.
DT_FMT = "%Y-%m-%d %H:%M:%S"


class DbHandler:
    """SQLite-backed persistence layer for the Habit Tracker."""

    def __init__(self, db_path: str | Path = "habit_tracker.db") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    periodicity TEXT NOT NULL CHECK(periodicity IN ('daily','weekly')),
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, name)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE
                )
            """)

    # ----------------------------
    # Users (NEW PUBLIC API)
    # ----------------------------

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=int(row["id"]),
            username=str(row["username"]),
            created_at=datetime.strptime(str(row["created_at"]), DT_FMT),
        )

    def create_user(self, username: str, created_at: datetime | None = None) -> User:
        created_at = created_at or datetime.now()
        username = username.strip()

        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO users (username, created_at) VALUES (?, ?)",
                (username, created_at.strftime(DT_FMT)),
            )
            uid = int(cur.lastrowid)

        return User(id=uid, username=username, created_at=created_at)

    def list_users(self) -> list[User]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM users ORDER BY id").fetchall()
        return [self._row_to_user(r) for r in rows]

    def get_user(self, user_id: int) -> User | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._row_to_user(row) if row else None

    def delete_user(self, user_id: int) -> None:
        # FK cascade should delete habits + completions
        with self._connect() as conn:
            conn.execute("DELETE FROM users WHERE id = ?", (user_id,))

    def _ensure_default_user(self) -> int:
        """
        Keep old behavior for the CLI: the app supports a single default user.
        If a user is not provided, we attach habits to the first user or create default_user.
        """
        with self._connect() as conn:
            row = conn.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
            if row:
                return int(row["id"])

            created_at = datetime.now().strftime(DT_FMT)
            cur = conn.execute(
                "INSERT INTO users (username, created_at) VALUES (?, ?)",
                ("default_user", created_at),
            )
            return int(cur.lastrowid)

    # ----------------------------
    # Habits
    # ----------------------------

    def _row_to_habit(self, row: sqlite3.Row) -> Habit:
        return Habit(
            id=int(row["id"]),
            name=str(row["name"]),
            description=str(row["description"]),
            periodicity=str(row["periodicity"]),  # type: ignore[arg-type]
            created_at=datetime.strptime(str(row["created_at"]), DT_FMT),
        )

    def create_habit(
        self,
        name: str,
        description: str,
        periodicity: Periodicity,
        created_at: datetime | None = None,
        user_id: int | None = None,
    ) -> Habit:
        """
        Create a habit. If user_id is None, attaches to default_user (backwards compatible).
        """
        created_at = created_at or datetime.now()
        user_id = user_id if user_id is not None else self._ensure_default_user()

        name = name.strip()
        description = description.strip()

        # optional safety check: user must exist
        if self.get_user(user_id) is None:
            raise ValueError(f"user_id={user_id} not found")

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO habits (user_id, name, description, periodicity, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, name, description, periodicity, created_at.strftime(DT_FMT)),
            )
            hid = int(cur.lastrowid)

        return Habit(hid, name, description, periodicity, created_at)

    def list_habits(self, user_id: int | None = None) -> list[Habit]:
        with self._connect() as conn:
            if user_id is None:
                rows = conn.execute("SELECT * FROM habits ORDER BY id").fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM habits WHERE user_id = ? ORDER BY id", (user_id,)
                ).fetchall()
        return [self._row_to_habit(r) for r in rows]

    def get_habit(self, habit_id: int, user_id: int | None = None) -> Habit | None:
        with self._connect() as conn:
            if user_id is None:
                row = conn.execute(
                    "SELECT * FROM habits WHERE id = ?", (habit_id,)
                ).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM habits WHERE id = ? AND user_id = ?",
                    (habit_id, user_id),
                ).fetchone()

        return self._row_to_habit(row) if row else None

    def delete_habit(self, habit_id: int, user_id: int | None = None) -> None:
        with self._connect() as conn:
            if user_id is None:
                conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
            else:
                conn.execute(
                    "DELETE FROM habits WHERE id = ? AND user_id = ?",
                    (habit_id, user_id),
                )

    # ----------------------------
    # Completions
    # ----------------------------

    def _period_id(self, created_at: datetime, period_days: int, ts: datetime) -> int:
        delta_days = (ts.date() - created_at.date()).days
        return -1 if delta_days < 0 else delta_days // period_days

    def _has_completion_in_period(self, habit: Habit, ts: datetime) -> bool:
        period_days = habit.period_length_days()
        target_pid = self._period_id(habit.created_at, period_days, ts)
        if target_pid < 0:
            return False

        completions = self.list_completions(habit_id=habit.id)
        existing_pids = set(
            self._period_id(habit.created_at, period_days, c.completed_at)
            for c in completions
        )
        return target_pid in existing_pids

    def add_completion(self, habit_id: int, when: datetime | None = None) -> bool:
        """
        Add a completion for a habit.

        Returns:
          True  -> completion saved
          False -> already completed in this period (or habit missing)
        """
        ts = when or datetime.now()
        habit = self.get_habit(habit_id)
        if habit is None:
            return False

        if self._has_completion_in_period(habit, ts):
            return False

        with self._connect() as conn:
            conn.execute(
                "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                (habit_id, ts.strftime(DT_FMT)),
            )
        return True

    def list_completions(self, habit_id: int | None = None) -> list[Completion]:
        with self._connect() as conn:
            if habit_id is None:
                rows = conn.execute(
                    "SELECT * FROM completions ORDER BY completed_at"
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM completions WHERE habit_id = ? ORDER BY completed_at",
                    (habit_id,),
                ).fetchall()

        return [
            Completion(
                id=int(r["id"]),
                habit_id=int(r["habit_id"]),
                completed_at=datetime.strptime(str(r["completed_at"]), DT_FMT),
            )
            for r in rows
        ]

    # ----------------------------
    # Seed
    # ----------------------------

    def seed_if_empty(self) -> None:
        """Seed 5 habits + 4 weeks of fixture data if DB is empty."""
        if self.list_habits():
            return

        user_id = self._ensure_default_user()

        start = (datetime.now() - timedelta(days=27)).replace(
            hour=18, minute=0, second=0, microsecond=0
        )

        h1 = self.create_habit(
            "Morning stretch", "5–10 min mobility routine.", "daily",
            created_at=start, user_id=user_id
        )
        h2 = self.create_habit(
            "No sugary drink", "Avoid soda/energy drinks.", "daily",
            created_at=start, user_id=user_id
        )
        h3 = self.create_habit(
            "Study session", "45 min focused study.", "daily",
            created_at=start, user_id=user_id
        )
        h4 = self.create_habit(
            "Weekly cleaning", "Clean room + laundry.", "weekly",
            created_at=start, user_id=user_id
        )
        h5 = self.create_habit(
            "Budget review", "Check spending & plan week.", "weekly",
            created_at=start, user_id=user_id
        )

        for day in range(28):
            d = start + timedelta(days=day)

            if day % 6 != 5:
                self.add_completion(h1.id, d)  # type: ignore[arg-type]
            if day % 4 != 3:
                self.add_completion(h2.id, d + timedelta(minutes=30))  # type: ignore[arg-type]
            if day % 3 != 2:
                self.add_completion(h3.id, d + timedelta(hours=1))  # type: ignore[arg-type]

            if day in (2, 9, 16, 23):
                self.add_completion(h4.id, d + timedelta(hours=2))  # type: ignore[arg-type]
            if day in (4, 11, 18):
                self.add_completion(h5.id, d + timedelta(hours=3))  # type: ignore[arg-type]
