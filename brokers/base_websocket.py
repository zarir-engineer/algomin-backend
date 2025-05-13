# brokers/base_websocket.py

from abc import ABC, abstractmethod

class BaseWebSocketClient(ABC):
    @abstractmethod
    def connect(self): pass

    @abstractmethod
    def subscribe(self, tokens: list): pass

    @abstractmethod
    def on_ticks(self, callback): pass

    @abstractmethod
    def run_forever(self): pass
