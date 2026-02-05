from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from src.models.habit import Habit, Periodicity
from src.models.completion import Completion

DT_FMT = "%Y-%m-%d %H:%M:%S"


class DbHandler:
    """Small SQLite repository for habits and completions."""

    def __init__(self, db_path: str | Path = "habit_tracker.db") -> None:
        self.db_path = str(db_path)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT NOT NULL,
                    periodicity TEXT NOT NULL CHECK(periodicity IN ('daily','weekly')),
                    created_at TEXT NOT NULL
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

    # ---------- habits ----------
    def create_habit(self, name: str, description: str, periodicity: Periodicity) -> Habit:
        created_at = datetime.now()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO habits (name, description, periodicity, created_at) VALUES (?, ?, ?, ?)",
                (name.strip(), description.strip(), periodicity, created_at.strftime(DT_FMT)),
            )
            hid = int(cur.lastrowid)
        return Habit(hid, name.strip(), description.strip(), periodicity, created_at)

    def list_habits(self) -> list[Habit]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM habits ORDER BY id").fetchall()
        return [self._row_to_habit(r) for r in rows]

    def get_habit(self, habit_id: int) -> Habit | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM habits WHERE id = ?", (habit_id,)).fetchone()
        return self._row_to_habit(row) if row else None

    def delete_habit(self, habit_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

    def _row_to_habit(self, row: sqlite3.Row) -> Habit:
        return Habit(
            id=int(row["id"]),
            name=str(row["name"]),
            description=str(row["description"]),
            periodicity=str(row["periodicity"]),  # type: ignore[arg-type]
            created_at=datetime.strptime(str(row["created_at"]), DT_FMT),
        )

    # ---------- completions ----------
    def add_completion(self, habit_id: int, when: datetime | None = None) -> Completion:
        ts = when or datetime.now()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO completions (habit_id, completed_at) VALUES (?, ?)",
                (habit_id, ts.strftime(DT_FMT)),
            )
            cid = int(cur.lastrowid)
        return Completion(cid, habit_id, ts)

    def list_completions(self, habit_id: int | None = None) -> list[Completion]:
        with self._connect() as conn:
            if habit_id is None:
                rows = conn.execute("SELECT * FROM completions ORDER BY completed_at").fetchall()
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

    # ---------- seed / fixture ----------
    def seed_if_empty(self) -> None:
        """
        IU requirement: provide 5 predefined habits (min. 1 daily + 1 weekly),
        plus example tracking data for 4 weeks.
        """
        if self.list_habits():
            return

        # Your own set of habits (different from your friend's list)
        h1 = self.create_habit("Morning stretch", "5–10 min mobility routine.", "daily")
        h2 = self.create_habit("No sugary drink", "Avoid soda/energy drinks.", "daily")
        h3 = self.create_habit("Study session", "45 min focused study.", "daily")
        h4 = self.create_habit("Weekly cleaning", "Clean room + laundry.", "weekly")
        h5 = self.create_habit("Budget review", "Check spending & plan week.", "weekly")

        # 4-week fixture: last 28 days, deterministic pattern with intentional misses
        start = (datetime.now() - timedelta(days=27)).replace(hour=18, minute=0, second=0, microsecond=0)

        for day in range(28):
            d = start + timedelta(days=day)

            # daily habits: varied completion patterns
            if day % 6 != 5:
                self.add_completion(h1.id, d)  # type: ignore[arg-type]
            if day % 4 != 3:
                self.add_completion(h2.id, d + timedelta(minutes=30))  # type: ignore[arg-type]
            if day % 3 != 2:
                self.add_completion(h3.id, d + timedelta(hours=1))  # type: ignore[arg-type]

            # weekly habits: once per week (with a missed week for realism)
            if day in (2, 9, 16, 23):
                self.add_completion(h4.id, d + timedelta(hours=2))  # type: ignore[arg-type]
            if day in (4, 11, 18):  # intentionally miss week 4
                self.add_completion(h5.id, d + timedelta(hours=3))  # type: ignore[arg-type]
