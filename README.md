# Habit Tracker CLI Application

Welcome to the **Habit Tracker** — a Python-based command-line interface (CLI) application for defining habits, checking them off periodically, and analysing habit streaks over time using analytics functions built on a functional programming approach.

This application was developed as part of the IU Portfolio Project for the module **DLBDSOOFPP01 – Object-Oriented and Functional Programming with Python**.

---

## Features

- Habit creation and deletion with **daily** and **weekly** periodicity  
- Habit completion (check-off) at any point in time  
- Enforcement of **one completion per habit per period**  
- Automatic streak tracking based on consecutive periods  
- Analytics functionality:
  - Longest streak for each habit
  - Longest streak overall
  - Habits due today
  - Habit filtering by periodicity
- Persistent storage using **SQLite**
- Predefined data with **5 habits** and **4 weeks of example tracking data**
- Built-in unit testing using **pytest**

---

## Technologies Used

- Python 3.11+
- SQLite for data storage
- Click for CLI interactions
- Pytest for unit testing
- Functional Programming using `map`, `filter`, and pure functions
- Modular Object-Oriented Programming structure

---

## Project Structure

```text
habit-tracker/
├── src/
│   ├── main.py                   # CLI entry point
│   ├── analytics/                # Functional analytics
│   │   └── analytics.py
│   ├── database/                 # SQLite handler
│   │   └── db_handler.py
│   ├── models/                   # Core classes
│   │   ├── habit.py
│   │   ├── user.py
│   │   └── completion.py
│   └── tests/                    # Unit tests
│       ├── test_analytics.py
│       ├── test_completions.py
│       ├── test_db_handler.py
│       ├── test_habits.py
│       └── test_users.py
```

---

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Direna88/habit-tracker.git
cd habit-tracker
```

### 2. Create and activate a virtual environment

```bash
python -m venv .habit
source .habit/Scripts/activate    # Windows (Git Bash)
# or
source .habit/bin/activate        # macOS / Linux
```

### 3. Install Dependencies

```bash
pip install click pytest
```

### 4. Launch the Application

Start by listing predefined habits:

```bash
python -m src.main list
```

---

## Creating a New Habit (Interactive)

The `create` command works interactively and prompts for input:

```bash
python -m src.main create
```

You will then be asked to enter:

```
Name:
Description:
Periodicity (daily, weekly):
```

Example:

```
Name: Drink water
Description: Drink more water
Periodicity (daily, weekly): daily
```

Verify creation:

```bash
python -m src.main list
```

---

## Mark a Habit as Completed

```bash
python -m src.main checkoff <habit_id>
```

Example:

```bash
python -m src.main checkoff 1
```

---

## Delete a Habit

```bash
python -m src.main delete <habit_id>
```

---

## Analytics Commands

```bash
python -m src.main analytics longest-overall
python -m src.main analytics longest 1
python -m src.main analytics period daily
python -m src.main analytics due-today
python -m src.main analytics streaks
```

The database and tables are created automatically when the application starts.  
The application is preloaded with 5 predefined habits and 4 weeks of example tracking data.

---

## Running Tests

```bash
pytest
```

This runs all unit tests across:

- Habit creation and validation rules  
- Completion rules (one completion per period)  
- Daily and weekly streak calculations  
- Database persistence and cascade delete behaviour  
- Analytics correctness  

All tests should pass successfully.

---

## Author

Direna Bashota  

Created for IU’s module  
**DLBDSOOFPP01 – Object-Oriented and Functional Programming with Python**
