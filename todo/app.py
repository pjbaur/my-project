import json
import os

DEFAULT_FILE = os.path.expanduser("~/.todo.json")


def _load(path=DEFAULT_FILE):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(tasks, path=DEFAULT_FILE):
    with open(path, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(name, path=DEFAULT_FILE):
    tasks = _load(path)
    tasks.append(name)
    _save(tasks, path)


def list_tasks(path=DEFAULT_FILE):
    return _load(path)


def remove_task(index, path=DEFAULT_FILE):
    tasks = _load(path)
    if index < 0 or index >= len(tasks):
        raise IndexError(f"index {index} out of range (0-{len(tasks) - 1})")
    removed = tasks.pop(index)
    _save(tasks, path)
    return removed
