# brokers/base_websocket_client.py

from abc import ABC, abstractmethod

class BaseWebSocketClient(ABC):
    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def subscribe(self, correlation_id: str, mode: str, token_list: list): pass

    @abstractmethod
    def set_callbacks(self, on_data, on_open, on_close, on_error): pass

    @abstractmethod
    def run_forever(self): pass

    @abstractmethod
    def close(self): pass


