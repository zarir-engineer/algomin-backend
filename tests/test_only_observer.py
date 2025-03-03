import json
from pymongo import MongoClient

# Observer Interface
class WebSocketObserver:
    def update(self, message):
        raise NotImplementedError("Observer must implement the update method.")

# Concrete Observer: Logs messages
class LoggerObserver(WebSocketObserver):
    def update(self, message):
        print("[Logger] Received:", message)

# Concrete Observer: Alerts on a certain condition
class AlertObserver(WebSocketObserver):
    def update(self, message):
        data = json.loads(message)
        if "price" in data and data["price"] > 1000:  # Example condition
            print("[Alert] Price exceeded 1000:", data["price"])

# Concrete Observer: Stores messages in MongoDB
class MongoDBObserver(WebSocketObserver):
    def __init__(self, db_url="mongodb://localhost:27017/", db_name="websocket_db", collection_name="messages"):
        self.client = MongoClient(db_url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def update(self, message):
        data = json.loads(message)
        self.collection.insert_one(data)
        print("[MongoDB] Stored message:", data)

# Subject: WebSocket Handler that notifies all observers
class WebSocketSubject:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer.update(message)

# Example Usage
if __name__ == "__main__":
    ws_subject = WebSocketSubject()

    # Create observers
    logger_observer = LoggerObserver()
    alert_observer = AlertObserver()
    mongo_observer = MongoDBObserver()

    # Register observers
    ws_subject.add_observer(logger_observer)  # Logs everything
    ws_subject.add_observer(alert_observer)   # Checks for alerts
    ws_subject.add_observer(mongo_observer)   # Stores in MongoDB

    # Simulate incoming WebSocket messages
    test_message1 = json.dumps({"price": 1050, "symbol": "AAPL"})
    test_message2 = json.dumps({"price": 900, "symbol": "GOOG"})

    # WebSocketSubject sends message to all observers
    ws_subject.notify_observers(test_message1)  # Logs, stores, and alerts
    ws_subject.notify_observers(test_message2)  # Logs and stores, but no alert
