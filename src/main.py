from __future__ import annotations

"""
Command-line interface for the Habit Tracker.

Uses `click` for a simple and discoverable CLI surface. The module
initializes a `DbHandler` instance against a top-level database file
and seeds example data for local development and demos.
"""

from pathlib import Path
import click

from src.database.db_handler import DbHandler
from src.analytics.analytics import (
    habits_by_periodicity,
    longest_streak_for,
    longest_streak_overall,
    habits_due_today,
    longest_streaks_per_habit,
)

# Default DB file next to the repository root; using a fixed path makes
# it obvious where data lives for the demo CLI. Tests create temporary
# DB files instead of using this path.
DB_PATH = Path(__file__).resolve().parent.parent / "habit_tracker.db"
db = DbHandler(str(DB_PATH))
# Seed demo data on first run to provide a pleasant out-of-the-box
# experience when running the CLI locally.
db.seed_if_empty()


@click.group()
def cli() -> None:
    """Habit Tracker CLI (IU portfolio project)."""
    pass


@cli.command("list")
def cmd_list() -> None:
    """List all habits."""
    habits = db.list_habits()
    if not habits:
        click.echo("No habits stored yet.")
        return
    for h in habits:
        click.echo(
            f"[{h.id:02d}] "
            f"{h.name:<20} | "
            f"{h.periodicity:<6} | "
            f"created {h.created_at.date()}"
        )


@cli.command("create")
@click.option("--name", prompt=True, help="Short habit name (task).")
@click.option("--description", prompt=True, help="More detail about the task.")
@click.option("--periodicity", type=click.Choice(["daily", "weekly"]), prompt=True)
def cmd_create(name: str, description: str, periodicity: str) -> None:
    """Create a new habit with a task description and periodicity."""
    h = db.create_habit(name=name, description=description, periodicity=periodicity)  # type: ignore[arg-type]
    click.echo(f"Created habit [{h.id}] {h.name} ({h.periodicity}).")


@cli.command("delete")
@click.argument("habit_id", type=int)
def cmd_delete(habit_id: int) -> None:
    """Delete a habit (and related completions)."""
    db.delete_habit(habit_id)
    click.echo(f"Deleted habit id={habit_id}.")


@cli.command("checkoff")
@click.argument("habit_id", type=int)
def cmd_checkoff(habit_id: int) -> None:
    """Mark a habit as completed for the current period."""
    habit = db.get_habit(habit_id)
    if habit is None:
        click.echo("Habit not found.")
        return

    saved = db.add_completion(habit_id)

    if saved:
        click.echo(f"Saved completion for: {habit.name}")
    else:
        click.echo(
            f"Already completed '{habit.name}' for the current {habit.periodicity} period."
        )


@cli.group("analytics")
def analytics() -> None:
    """Run analytics queries."""
    pass


@analytics.command("period")
@click.argument("periodicity", type=click.Choice(["daily", "weekly"]))
def a_period(periodicity: str) -> None:
    """List habits filtered by periodicity."""
    habits = habits_by_periodicity(db.list_habits(), periodicity)
    for h in habits:
        click.echo(f"[{h.id}] {h.name} ({h.periodicity})")


@analytics.command("longest-overall")
def a_longest_overall() -> None:
    """Show the habit with the longest streak overall."""
    habits = db.list_habits()
    comps = db.list_completions()
    h, streak = longest_streak_overall(habits, comps)
    if h is None:
        click.echo("No habits.")
    else:
        click.echo(f"Longest overall streak: {h.name} → {streak} periods")


@analytics.command("longest")
@click.argument("habit_id", type=int)
def a_longest(habit_id: int) -> None:
    """Show the longest streak for a single habit."""
    habit = db.get_habit(habit_id)
    if habit is None:
        click.echo("Habit not found.")
        return
    comps = db.list_completions(habit_id=habit_id)
    streak = longest_streak_for(habit, comps)
    click.echo(f"Longest streak for {habit.name}: {streak} periods")


@analytics.command("streaks")
def a_streaks() -> None:
    """Show longest streak for every habit."""
    habits = db.list_habits()
    comps = db.list_completions()
    rows = longest_streaks_per_habit(habits, comps)
    for h, s in rows:
        click.echo(f"[{h.id}] {h.name} ({h.periodicity}) → longest streak: {s} periods")


@analytics.command("due-today")
def a_due_today() -> None:
    """Show habits that are due in the current period."""
    habits = db.list_habits()
    comps = db.list_completions()
    due = habits_due_today(habits, comps)

    if not due:
        click.echo("No habits due right now. Well done!!")
    else:
        click.echo("Habits due now:")
        for h in due:
            click.echo(f"- [{h.id}] {h.name} ({h.periodicity})")


def main() -> None:
    cli(prog_name="habit-tracker")


if __name__ == "__main__":
    main()
