import argparse
import sys

from todo.app import add_task, list_tasks, remove_task


def main(argv=None):
    parser = argparse.ArgumentParser(prog="todo", description="Simple CLI todo manager")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Add a task")
    p_add.add_argument("name", help="Task description")

    p_list = sub.add_parser("list", help="List all tasks")

    p_rm = sub.add_parser("remove", help="Remove a task by index")
    p_rm.add_argument("index", type=int, help="Task index to remove")

    args = parser.parse_args(argv)

    if args.command == "add":
        add_task(args.name)
        print(f"Added: {args.name}")
    elif args.command == "list":
        tasks = list_tasks()
        if not tasks:
            print("No tasks.")
            return
        for i, t in enumerate(tasks):
            print(f"  {i}: {t}")
    elif args.command == "remove":
        try:
            removed = remove_task(args.index)
            print(f"Removed: {removed}")
        except IndexError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
