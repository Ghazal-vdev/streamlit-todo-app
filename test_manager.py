# Basic tests for the Task Master project.
# Note: test_export_to_json and test_send_to_server use the real tasks.db,
# so add a few tasks in the app before running them.
# test_send_to_server also needs an internet connection.

from MyTasks import TodoManager
import pytest
import json
import requests


@pytest.fixture  # builds a temporary db, so the tests don't touch the real one
def manager(tmp_path):
    # tmp_path is a temporary folder that pytest creates automatically
    return TodoManager(str(tmp_path / 'test_tasks.db'))


def test_export_to_json():
    manager = TodoManager('tasks.db')
    tasks_data = manager.get_tasks_with_list_names()

    json_output = json.dumps(tasks_data, indent=4, ensure_ascii=False)

    with open('exported_tasks.json', mode='w', encoding='utf-8') as f:
        f.write(json_output)

    parsed = json.loads(json_output)
    assert isinstance(parsed, list)
    if parsed:  # safety check
        assert "id" in parsed[0]


def test_send_to_server():
    manager = TodoManager('tasks.db')
    tasks_data = manager.get_tasks_with_list_names()
    assert tasks_data, "No data to send."

    url = "https://jsonplaceholder.typicode.com/posts"
    response = requests.post(url, json=tasks_data)

    assert response.status_code == 201
    body = response.json()
    assert 'id' in body


def test_full_workflow_integration(manager):
    # 1. create a list and add a task to it
    manager.create_list("Test")
    list_id = manager.get_all_lists()[0]["id"]

    success, message = manager.add_task(list_id=list_id,
                                        task_content="Integration Test Task",
                                        priority=1, due_hour=13, is_done=0)
    assert success is True, f"Failed to add task: {message}"

    # 2. check that the task is saved in the database
    tasks = manager.get_tasks_with_list_names()
    assert any(t['task_content'] == "Integration Test Task" for t in tasks), \
        "Error: Task wasn't found in DB after adding."

    # 3. find the id of the added task (don't rely on a fixed id)
    target_task = next(t for t in tasks if t['task_content'] == "Integration Test Task")
    target_id = target_task['id']

    # 4. mark the task as done
    success, message = manager.toggle_task_status(target_id, 1)
    assert success is True, f"Failed to toggle task: {message}"

    # 5. check that the status changed
    tasks = manager.get_tasks_with_list_names()
    done_task = next(t for t in tasks if t['id'] == target_id)
    assert done_task['is_done'] == 1