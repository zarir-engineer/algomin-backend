import unittest
from base.advanced_line_command import main

class TestCLI(unittest.TestCase):

    def test_add_command(self):
        """Test the 'add' command."""
        result = main(["add", "apple"])
        self.assertEqual(result, "Adding item: apple")

    def test_remove_command(self):
        """Test the 'remove' command."""
        result = main(["remove", "banana"])
        self.assertEqual(result, "Removing item: banana")

    def test_missing_command(self):
        """Test if missing command raises a SystemExit."""
        with self.assertRaises(SystemExit):
            main([])  # No command provided

    def test_missing_argument(self):
        """Test if missing argument raises a SystemExit."""
        with self.assertRaises(SystemExit):
            main(["add"])  # Missing item argument

if __name__ == "__main__":
    unittest.main()
