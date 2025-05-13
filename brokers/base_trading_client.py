# brokers/base_trading_client.py

from abc import ABC, abstractmethod

class BaseTradingClient(ABC):
    @abstractmethod
    def place_order(self, order_data: dict) -> dict:
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> dict:
        pass

    @abstractmethod
    def modify_order(self, order_id: str, changes: dict) -> dict:
        pass

    @abstractmethod
    def get_positions(self) -> list:
        pass

    @abstractmethod
    def get_holdings(self) -> list:
        pass
