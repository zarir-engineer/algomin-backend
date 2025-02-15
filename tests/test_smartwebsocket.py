#####################################################
# $ > cd main_project_dir
# command: python -m unittest tests.test_smartwebsocket
#####################################################


import unittest
from unittest.mock import patch
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from base import config as cnf
from base.session import Session


class TestSmartWebSocketV2(unittest.TestCase):
    sess = Session()
    AUTH_TOKEN = sess.auth_token()
    FEED_TOKEN = sess.feed_token()

    def setUp(self):
        """Set up a mocked SmartWebSocketV2 instance before each test"""
        self.auth_token = self.AUTH_TOKEN
        self.feed_token = self.FEED_TOKEN
        self.api_key = cnf.API_KEY
        self.client_id = cnf.CLIENT_ID

        # Create a SmartWebSocketV2 instance with mock parameters
        self.sws = SmartWebSocketV2(
            self.auth_token,
            self.api_key,
            self.client_id,
            self.feed_token,
            max_retry_attempt=5
        )

    @patch("SmartApi.smartWebSocketV2.SmartWebSocketV2.connect")
    def test_websocket_connect(self, mock_connect):
        """Test WebSocket connection method"""
        mock_connect.return_value = None  # Mock connect() to do nothing

        self.sws.connect()
        mock_connect.assert_called_once()  # Verify connect() was called once

    @patch("SmartApi.smartWebSocketV2.SmartWebSocketV2.subscribe")
    def test_websocket_subscribe(self, mock_subscribe):
        """Test WebSocket subscription"""
        token_list = [{"exchangeType": 2, "tokens": ["57920"]}]
        mock_subscribe.return_value = None  # Mock subscribe()

        self.sws.subscribe(token_list)
        mock_subscribe.assert_called_once_with(token_list)  # Verify subscribe() call

    @patch("SmartApi.smartWebSocketV2.SmartWebSocketV2.unsubscribe")
    def test_websocket_unsubscribe(self, mock_unsubscribe):
        """Test WebSocket unsubscription"""
        token_list = [{"exchangeType": 2, "tokens": ["57920"]}]
        mock_unsubscribe.return_value = None  # Mock unsubscribe()

        self.sws.unsubscribe(token_list)
        mock_unsubscribe.assert_called_once_with(token_list)  # Verify unsubscribe() call

    @patch("SmartApi.smartWebSocketV2.SmartWebSocketV2.close_connection")
    def test_websocket_disconnect(self, mock_close):
        """Test WebSocket disconnection"""
        mock_close.return_value = None  # Mock close_connection()
        # SmartWebSocketV2.on_close = custom_on_close

        self.sws.close_connection()
        mock_close.assert_called_once()  # Verify close_connection() was called

    # def custom_on_close(self, message):
    #     print("Custom on_message handler")
    #     # Original functionality can be called if needed
    #     close logfile here if open

if __name__ == '__main__':
    unittest.main()
