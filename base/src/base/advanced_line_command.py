import argparse

def add_command(args):
    """Logic for the 'add' command"""
    return f"Adding item: {args.item}"

def remove_command(args):
    """Logic for the 'remove' command"""
    return f"Removing item: {args.item}"

def create_parser():
    """Creates and returns the argument parser."""
    parser = argparse.ArgumentParser(description="Example CLI using the Command Pattern")
    subparsers = parser.add_subparsers(dest='command', required=True, help="Available commands")

    # 'add' command
    parser_add = subparsers.add_parser('add', help="Add an item")
    parser_add.add_argument('item', type=str, help="The item to add")
    parser_add.set_defaults(func=add_command)

    # 'remove' command
    parser_remove = subparsers.add_parser('remove', help="Remove an item")
    parser_remove.add_argument('item', type=str, help="The item to remove")
    parser_remove.set_defaults(func=remove_command)

    return parser

def main(args=None):
    """Parses arguments and dispatches the command."""
    parser = create_parser()
    args = parser.parse_args(args)  # Accepts args for testing
    return args.func(args)  # Call the appropriate function

if __name__ == '__main__':
    print(main())  # Print result in real CLI usage
