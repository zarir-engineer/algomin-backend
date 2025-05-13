# sessions/base_session.py
from abc import ABC, abstractmethod

class BaseBrokerSession(ABC):
    @abstractmethod
    def get_auth_info(self) -> dict:
        pass
