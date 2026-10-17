# A Minimal Todo-list (OOP)

from datetime import datetime
import sqlite3
import logging

# logging.ERROR only logs error. (DEBUG < INFO < WARNING < ERROR < CRITICAL)
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s -\
                     - %(message)s -%(filename)s - %(lineno)d')


class TodoManager:
    def __init__(self, db_path = 'tasks.db'):
        self.db_path = db_path
        self._setup_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


    def _setup_db(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # table 1: Lists (parent)
            cursor.execute("""CREATE TABLE IF NOT EXISTS lists(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
            )STRICT;""")

            # table 2: Tasks (child)
            cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            list_id INTEGER NOT NULL,
            task_content TEXT NOT NULL,
            priority INTEGER DEFAULT 1,
            due_hour INTEGER,
            is_done INTEGER DEFAULT 0,
            done_at TEXT,
            FOREIGN KEY (list_id) REFERENCES lists (id) ON DELETE CASCADE
            ) STRICT;""")

    def create_list(self, name: str):
        name = name.strip()

        if not name:
            return False, "Choose a name for your list please."
        try:
            with self._get_connection() as conn:
            
                cursor = conn.cursor()
                cursor.execute("INSERT INTO lists(name) VALUES(?)", (name,))

                return True, f"List {name} created successfully! ✅"
            
        except sqlite3.IntegrityError:
            return False, "Name is taken. Choose another one."

        except Exception as e:

            logging.error(f"An unexpeted error has occurred: {e}")
            return False, "An internal error has occurred. Please try again later."

    def delete_list(self, id: int):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM lists WHERE id = ?", (id,))
                if cursor.rowcount == 0:
                    return False, "No list found with this id."
                return True, "List deleted successfully. ✅"

        except sqlite3.IntegrityError:
            return False, "Invalid list id."
        # Setting exc_info to True will cause the logging to include the full stack trace.
        except Exception as e:
            logging.error(f"An unexpected error has occurred: {e}", exc_info=True) 
            return False, "An internal error has occurred. Please try again later."

    def search_list_by_name(self, name: str):
        name = name.strip().lower()
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT # from lists WHERE name = ?", (name,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logging.error(f"An unexpected error has occurred: {e}", exc_info=True)
            return []

            

    def add_task(self, list_id, task_content, priority, due_hour, is_done):

        task_content = task_content.strip()
        
        if not task_content:
            return False, "Task content cannot be empty."
        try:
            with self._get_connection() as conn:

                cursor = conn.cursor()
                cursor.execute("INSERT INTO tasks(list_id, task_content, priority, due_hour, is_done)" \
                " VALUES(?,?,?,?,?)", (list_id, task_content, priority, due_hour, is_done))

                return True, "Task saved successfully.✅"
            
        except sqlite3.IntegrityError:
            return False, "Invalid list ID."

        except Exception as e:
            logging.info(f"An unexpected error has occurred: {e}", exc_info=True)
            return False, "An internal error has occurred. Please try again later."

    def delete_task(self, task_id: int):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                if cursor.rowcount == 0:
                    return False, "No task found with this id."
                return True, f"Task {task_id} successfully deleted. ✅"
            
        except sqlite3.IntegrityError:
            return False, "Invalid task id."
        
        except Exception as e:
            logging.error(f"An unexpected error has occurred: {e}", exc_info=True)
            return False, "An internal error has occurred. Please try again."

            
    def toggle_task_status(self, task_id: int, new_status: int):
        try:
            with self._get_connection() as conn:

                cursor = conn.cursor()

                if new_status == 1:
                    done_at_value = datetime.now().isoformat()
                else:
                    done_at_value = None

                cursor.execute("UPDATE tasks SET is_done = ?, done_at = ? WHERE id = ?", 
                               (new_status, done_at_value, task_id))
                if cursor.rowcount == 0:
                    return False, "No task found with this id."
                return True, "Task status updated."


        except sqlite3.IntegrityError:
            return False, "Invalid task id."

        except Exception as e:
            logging.error(f"An unexpeted error has occurred: {e}", exc_info=True)
            return False, "An internal error has occurred. Please try again later."
        



    def get_all_lists(self):
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM lists")
                rows = cursor.fetchall()
                return [{"id": r[0], "name": r[1]} for r in rows]
        except Exception as e:
            logging.error(f"Error fetching lists: {e}")
            return []

                        

    def get_tasks_by_list(self, list_id: int):
        try:
            with self._get_connection() as conn:

                conn.row_factory = sqlite3.Row # makes dict-like object instead of tuple
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM tasks WHERE list_id = ?", (list_id,))
                rows = cursor.fetchall()
                if not rows:
                    return []

                return [dict(row) for row in rows]
# makes datas portable by converting sqlite.Row(a special object of sqlite library) to a standard Python dict.
            
        except sqlite3.IntegrityError:
            return False, "Invalid list id."
        
        except Exception as e:
            logging.error(f"An unexpected error has occured: {e}", exc_info=True)
            return []
        
    def get_tasks_with_list_names(self): # using JOIN for the first time
        try:
            with self._get_connection() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

            # in order to show the empty lists we need to use LEFT JOIN instead of INNER JOIN.
                query = """ 
                SELECT
                    tasks.id,
                    tasks.task_content,
                    tasks.priority,
                    tasks.is_done,
                    lists.name AS list_name
                FROM lists
                LEFT JOIN tasks 
                ON tasks.list_id = lists.id
                """

                cursor.execute(query)
                rows = cursor.fetchall()

                return [dict(row) for row in rows]

        except Exception as e:
            logging.error(f"An unexpected error has occurred: {e}", exc_info=True)
            return []