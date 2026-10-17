# 🚀 Task Master

A task management web app built with Python, Streamlit, and SQLite.

## Features
- Create and delete task lists
- Add tasks with a priority (Low / Medium / High) and a due hour
- Mark tasks as done or undone
- Dashboard with total, completed, and pending counts
- Export reports as CSV or Excel
- Error logging to a log file

## Tech Stack
- Python
- Streamlit (user interface)
- SQLite (database, foreign keys with cascade delete)
- pandas (data tables and exports)
- Object-Oriented Programming (`TodoManager` class)

## Project Structure
```
app.py                # Streamlit user interface
MyTasks.py            # TodoManager class: all database operations
test_manager.py     # Basic pytest tests
requirements.txt      # Dependencies
```
The database (`tasks.db`) and the log file (`app.log`) are created automatically on first run.

## How to Run
1. Clone the repository:
```
   git clone https://github.com/Ghazal-vdev/streamlit-todo-app.git
   cd streamlit-todo-app
```
2. Create a virtual environment and install the requirements:
```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
```
3. Start the app:
```
   streamlit run app.py
```
## Run the Tests
```
pytest
```
The first two tests read the local `tasks.db`, so add a few tasks in the app first. The server test needs an internet connection.

## What I Practiced
- Designing a relational database with two tables (lists and tasks) and a JOIN
- Separating the interface from the database logic
- Error handling and logging
- Exporting data with pandas
- Writing basic tests with pytest (temporary database fixture, JSON export).