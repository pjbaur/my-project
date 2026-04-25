import json
import os
import tempfile
import unittest
from unittest.mock import patch

from todo.app import add_task, list_tasks, remove_task


class TestTodo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_add_and_list(self):
        add_task("buy milk", self.path)
        add_task("walk dog", self.path)
        self.assertEqual(list_tasks(self.path), ["buy milk", "walk dog"])

    def test_persistence(self):
        add_task("task one", self.path)
        # Re-read from file
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(data, ["task one"])

    def test_remove(self):
        add_task("a", self.path)
        add_task("b", self.path)
        removed = remove_task(0, self.path)
        self.assertEqual(removed, "a")
        self.assertEqual(list_tasks(self.path), ["b"])

    def test_remove_out_of_range(self):
        add_task("only", self.path)
        with self.assertRaises(IndexError):
            remove_task(5, self.path)

    def test_empty_list(self):
        self.assertEqual(list_tasks(self.path), [])

    def test_missing_file_returns_empty(self):
        self.assertEqual(list_tasks("/nonexistent/path.json"), [])


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_cli_add_list(self):
        from todo.cli import main

        with patch("todo.cli.add_task") as mock_add:
            main(["add", "test task"])
            mock_add.assert_called_once_with("test task")


if __name__ == "__main__":
    unittest.main()
