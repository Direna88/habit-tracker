from __future__ import annotations

import click

from src.database.db_handler import DbHandler
from src.analytics.analytics import (
    all_habits,
    habits_by_periodicity,
    longest_streak_for,
    longest_streak_overall,
)

db = DbHandler("habit_tracker.db")
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
    db.add_completion(habit_id)
    click.echo(f"Saved completion for: {habit.name}")


@cli.group("analytics")
def analytics() -> None:
    """Run analytics queries."""
    pass


@analytics.command("all")
def a_all() -> None:
    habits = all_habits(db.list_habits())
    for h in habits:
        click.echo(f"[{h.id}] {h.name} ({h.periodicity})")


@analytics.command("period")
@click.argument("periodicity", type=click.Choice(["daily", "weekly"]))
def a_period(periodicity: str) -> None:
    habits = habits_by_periodicity(db.list_habits(), periodicity)
    for h in habits:
        click.echo(f"[{h.id}] {h.name} ({h.periodicity})")


@analytics.command("longest-overall")
def a_longest_overall() -> None:
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
    habit = db.get_habit(habit_id)
    if habit is None:
        click.echo("Habit not found.")
        return
    comps = db.list_completions(habit_id=habit_id)
    streak = longest_streak_for(habit, comps)
    click.echo(f"Longest streak for {habit.name}: {streak} periods")


if __name__ == "__main__":
    cli()
