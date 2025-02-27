# python -m unittest your_test_file.py

import json
import unittest
from unittest.mock import patch
from collections import deque
import datetime
import pytz

# Import the classes
from live.observer_live_api import LoggerObserver, AlertObserver, EmailAlertObserver, MongoDBObserver, SmartWebSocketV2Client

class TestObservers(unittest.TestCase):

    @patch('builtins.print')
    def test_logger_observer(self, mock_print):
        observer = LoggerObserver()
        observer.update("Test Message")

        mock_print.assert_called_with("[Logger] Received:", "Test Message")

    @patch('builtins.print')
    def test_alert_observer(self, mock_print):
        observer = AlertObserver()

        message = json.dumps({"price": 1500})
        observer.update(message)

        mock_print.assert_called_with('+++ data ', {"price": 1500})
        # Uncomment below if you want to check alert logic
        # mock_print.assert_any_call("[Alert] Price exceeded 1000:", 1500)

    @patch('builtins.print')
    def test_email_alert_observer(self, mock_print):
        observer = EmailAlertObserver()
        message = json.dumps({"price": 1500})
        observer.update(message)
        mock_print.assert_called_with('[Email Alert] Sending email to pvhatkar@gmail.com: Price has exceeded 1000. Current price: 1500')

    @patch('builtins.print')
    def test_mongodb_observer(self, mock_print):
        observer = MongoDBObserver()
        message = json.dumps({"price": 1500})
        observer.update(message)
        mock_print.assert_called_with("[MongoDB] Message saved:", message)

class TestSmartWebSocketV2Client(unittest.TestCase):

    def setUp(self):
        self.client = SmartWebSocketV2Client()
        self.logger_observer = LoggerObserver()
        self.alert_observer = AlertObserver()

    def test_add_observer(self):
        self.client.add_observer(self.logger_observer)
        self.client.add_observer(self.alert_observer)

        self.assertIn(self.logger_observer, self.client.observers)
        self.assertIn(self.alert_observer, self.client.observers)

    @patch.object(LoggerObserver, 'update')
    @patch.object(AlertObserver, 'update')
    def test_notify_observers(self, mock_alert_update, mock_logger_update):
        self.client.add_observer(self.logger_observer)
        self.client.add_observer(self.alert_observer)

        test_message = json.dumps({"price": 1200})

        self.client.notify_observers(test_message)

        mock_logger_update.assert_called_with(test_message)
        mock_alert_update.assert_called_with(test_message)

class TestTimestampConversion(unittest.TestCase):

    def test_time_stamp_conversion(self):
        client = SmartWebSocketV2Client()
        test_message = {"exchange_timestamp": 1700000000000}  # Milliseconds

        expected_time = datetime.datetime.utcfromtimestamp(1700000000).replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

        result = client.time_stamp(None, test_message)

        self.assertEqual(result, expected_time)

if __name__ == '__main__':
    unittest.main()
