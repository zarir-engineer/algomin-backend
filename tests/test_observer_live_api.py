#####################################################
# This setup uses unittest.mock.patch to replace the on_*
# methods with mock objects, allowing you to test their
# invocation without executing their actual implementations.
# $ > cd main_project_dir
# command: python -m unittest tests.test_observer_api_live

# Inheritance is straightforward and leverages object-oriented principles
# but may not be suitable if the class is not designed for extension or
# if you need to change behavior dynamically.

#
# Monkey Patching allows for dynamic changes but can lead to maintenance
# challenges and unexpected behavior, especially if multiple patches are
# applied.
#
# The Decorator Pattern provides flexibility and adheres to the Single
# Responsibility Principle, allowing behavior to be added dynamically
# without modifying the original class.
#####################################################

import unittest
from unittest.mock import patch
from core.websocket_client import SmartWebSocketV2Client

class TestSmartWebSocketV2(unittest.TestCase):
    def setUp(self):
        # Initialize the SmartWebSocketV2 instance
        # self.ws = SmartWebSocketV2()
        self.ws = SmartWebSocketV2Client()

    def test_on_data(self):
        with patch.object(self.ws, 'on_data', return_value=None) as mock_on_data:
            self.ws.on_data('test message on data')
            mock_on_data.assert_called_once_with('test message on data')

    def test_on_open(self):
        # Test the on_open method
        with patch.object(self.ws, 'on_open', return_value=None) as mock_on_open:
            self.ws.on_open()
            mock_on_open.assert_called_once()

    def test_on_message(self):
        # Test the on_message method
        with patch.object(self.ws, 'on_message', return_value=None) as mock_on_message:
            self.ws.on_message('test message')
            mock_on_message.assert_called_once_with('test message')

    def test_on_error(self):
        # Test the on_error method
        with patch.object(self.ws, 'on_error', return_value=None) as mock_on_error:
            self.ws.on_error('test error')
            mock_on_error.assert_called_once_with('test error')

    def test_on_close(self):
        # Test the on_close method
        with patch.object(self.ws, 'on_close', return_value=None) as mock_on_close:
            self.ws.on_close()
            mock_on_close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
