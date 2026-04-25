import json
import os
import tempfile
import unittest
from unittest.mock import patch

from todo.app import add_task, list_tasks, remove_task
from todo.cli import main


class TestAddTask(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_add_single_task(self):
        add_task("buy milk", self.path)
        self.assertEqual(list_tasks(self.path), ["buy milk"])

    def test_add_multiple_tasks(self):
        add_task("first", self.path)
        add_task("second", self.path)
        add_task("third", self.path)
        self.assertEqual(list_tasks(self.path), ["first", "second", "third"])

    def test_add_duplicate_tasks(self):
        add_task("same", self.path)
        add_task("same", self.path)
        self.assertEqual(list_tasks(self.path), ["same", "same"])

    def test_add_empty_name(self):
        add_task("", self.path)
        self.assertEqual(list_tasks(self.path), [""])

    def test_add_whitespace_name(self):
        add_task("   ", self.path)
        self.assertEqual(list_tasks(self.path), ["   "])

    def test_add_special_characters(self):
        add_task("task with 'quotes' and \"doubles\"", self.path)
        self.assertEqual(list_tasks(self.path), ["task with 'quotes' and \"doubles\""])

    def test_add_unicode(self):
        add_task("Aufgabe 📋", self.path)
        self.assertEqual(list_tasks(self.path), ["Aufgabe 📋"])

    def test_add_long_task_name(self):
        name = "x" * 1000
        add_task(name, self.path)
        self.assertEqual(list_tasks(self.path), [name])


class TestListTasks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_empty_list(self):
        self.assertEqual(list_tasks(self.path), [])

    def test_single_task(self):
        add_task("only one", self.path)
        self.assertEqual(list_tasks(self.path), ["only one"])

    def test_multiple_tasks(self):
        tasks = ["alpha", "beta", "gamma"]
        for t in tasks:
            add_task(t, self.path)
        self.assertEqual(list_tasks(self.path), tasks)

    def test_missing_file_returns_empty(self):
        self.assertEqual(list_tasks("/nonexistent/path.json"), [])

    def test_empty_file_returns_empty(self):
        with open(self.path, "w") as f:
            f.write("")
        self.assertEqual(list_tasks(self.path), [])

    def test_corrupted_json_returns_empty(self):
        with open(self.path, "w") as f:
            f.write("{not valid json")
        self.assertEqual(list_tasks(self.path), [])

    def test_non_list_json_returns_dict(self):
        with open(self.path, "w") as f:
            json.dump({"key": "value"}, f)
        result = list_tasks(self.path)
        self.assertIsInstance(result, dict)

    def test_list_returns_copy(self):
        add_task("task", self.path)
        result = list_tasks(self.path)
        result.append("extra")
        self.assertEqual(list_tasks(self.path), ["task"])


class TestRemoveTask(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_remove_first(self):
        add_task("a", self.path)
        add_task("b", self.path)
        add_task("c", self.path)
        removed = remove_task(0, self.path)
        self.assertEqual(removed, "a")
        self.assertEqual(list_tasks(self.path), ["b", "c"])

    def test_remove_last(self):
        add_task("a", self.path)
        add_task("b", self.path)
        removed = remove_task(1, self.path)
        self.assertEqual(removed, "b")
        self.assertEqual(list_tasks(self.path), ["a"])

    def test_remove_middle(self):
        add_task("a", self.path)
        add_task("b", self.path)
        add_task("c", self.path)
        removed = remove_task(1, self.path)
        self.assertEqual(removed, "b")
        self.assertEqual(list_tasks(self.path), ["a", "c"])

    def test_remove_only_task(self):
        add_task("solo", self.path)
        removed = remove_task(0, self.path)
        self.assertEqual(removed, "solo")
        self.assertEqual(list_tasks(self.path), [])

    def test_remove_negative_index_raises(self):
        add_task("task", self.path)
        with self.assertRaises(IndexError):
            remove_task(-1, self.path)

    def test_remove_out_of_range(self):
        add_task("only", self.path)
        with self.assertRaises(IndexError):
            remove_task(5, self.path)

    def test_remove_from_empty_list(self):
        with self.assertRaises(IndexError):
            remove_task(0, self.path)

    def test_remove_index_equal_to_length(self):
        add_task("one", self.path)
        with self.assertRaises(IndexError):
            remove_task(1, self.path)


class TestPersistence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_save_load_roundtrip(self):
        add_task("first", self.path)
        add_task("second", self.path)
        with open(self.path) as f:
            data = json.load(f)
        self.assertEqual(data, ["first", "second"])

    def test_json_format_is_array(self):
        add_task("task", self.path)
        with open(self.path) as f:
            data = json.load(f)
        self.assertIsInstance(data, list)

    def test_file_created_on_first_add(self):
        os.unlink(self.path)
        self.assertFalse(os.path.exists(self.path))
        add_task("first", self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_empty_file_treated_as_empty_list(self):
        with open(self.path, "w") as f:
            f.write("")
        self.assertEqual(list_tasks(self.path), [])

    def test_corrupted_file_treated_as_empty_list(self):
        with open(self.path, "w") as f:
            f.write("not json at all")
        self.assertEqual(list_tasks(self.path), [])


class TestCLIAdd(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        self.path = self.tmp.name

    def tearDown(self):
        os.unlink(self.path)

    def test_add_prints_confirmation(self):
        with patch("todo.cli.add_task"):
            with patch("builtins.print") as mock_print:
                main(["add", "test task"])
                mock_print.assert_called_with("Added: test task")

    def test_add_calls_add_task(self):
        with patch("todo.cli.add_task") as mock_add:
            main(["add", "my task"])
            mock_add.assert_called_once_with("my task")


class TestCLIList(unittest.TestCase):
    def test_list_empty(self):
        with patch("todo.cli.list_tasks", return_value=[]):
            with patch("builtins.print") as mock_print:
                main(["list"])
                mock_print.assert_called_with("No tasks.")

    def test_list_with_tasks(self):
        with patch("todo.cli.list_tasks", return_value=["alpha", "beta"]):
            with patch("builtins.print") as mock_print:
                main(["list"])
                calls = mock_print.call_args_list
                self.assertEqual(calls[0], (("  0: alpha",),))
                self.assertEqual(calls[1], (("  1: beta",),))


class TestCLIRemove(unittest.TestCase):
    def test_remove_success(self):
        with patch("todo.cli.remove_task", return_value="done"):
            with patch("builtins.print") as mock_print:
                main(["remove", "2"])
                mock_print.assert_called_with("Removed: done")

    def test_remove_out_of_range_exits_1(self):
        with patch("todo.cli.remove_task", side_effect=IndexError("bad")):
            with self.assertRaises(SystemExit) as ctx:
                main(["remove", "99"])
            self.assertEqual(ctx.exception.code, 1)

    def test_remove_calls_with_int(self):
        with patch("todo.cli.remove_task", return_value="item") as mock_rm:
            with patch("builtins.print"):
                main(["remove", "3"])
                mock_rm.assert_called_once_with(3)


class TestCLINoCommand(unittest.TestCase):
    def test_no_args_prints_help_to_stdout(self):
        with patch("sys.stdout") as mock_stdout:
            main([])
            mock_stdout.write.assert_called()


if __name__ == "__main__":
    unittest.main()
