import unittest
from base.simple_line_command import parse_args

class TestArgumentParser(unittest.TestCase):

    def test_required_argument(self):
        """Test if the parser correctly handles required arguments."""
        args = parse_args(["--name", "Alice"])
        self.assertEqual(args.name, "Alice")
        self.assertEqual(args.age, 18)  # Default value

    def test_optional_argument(self):
        """Test if optional argument works correctly."""
        args = parse_args(["--name", "Bob", "--age", "25"])
        self.assertEqual(args.name, "Bob")
        self.assertEqual(args.age, 25)

    def test_missing_required_argument(self):
        """Test if missing required argument raises a SystemExit."""
        with self.assertRaises(SystemExit):  # argparse exits on error
            parse_args([])

if __name__ == "__main__":
    unittest.main()
