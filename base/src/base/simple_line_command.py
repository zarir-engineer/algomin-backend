import argparse

def create_parser():
    parser = argparse.ArgumentParser(description="Example ArgumentParser script.")
    parser.add_argument("--name", required=True, help="Your name")
    parser.add_argument("--age", type=int, default=18, help="Your age (default: 18)")
    return parser

def parse_args(args=None):
    parser = create_parser()
    return parser.parse_args(args)

if __name__ == "__main__":
    args = parse_args()
    print(f"Hello {args.name}, you are {args.age} years old.")
