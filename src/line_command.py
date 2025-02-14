import argparse

def add_command(args):
    # Logic for the "add" command
    print(f"Adding item: {args.item}")

def remove_command(args):
    # Logic for the "remove" command
    print(f"Removing item: {args.item}")

def main():
    parser = argparse.ArgumentParser(description="Example CLI using the Command Pattern")
    subparsers = parser.add_subparsers(dest='command', required=True,
                                       help="Available commands")

    # Subparser for the 'add' command
    parser_add = subparsers.add_parser('add', help="Add an item")
    parser_add.add_argument('item', type=str, help="The item to add")
    parser_add.set_defaults(func=add_command)  # Set the handler for 'add'

    # Subparser for the 'remove' command
    parser_remove = subparsers.add_parser('remove', help="Remove an item")
    parser_remove.add_argument('item', type=str, help="The item to remove")
    parser_remove.set_defaults(func=remove_command)  # Set the handler for 'remove'

    # Parse arguments and dispatch to the appropriate command handler
    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
