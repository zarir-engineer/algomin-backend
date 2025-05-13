# brokers/mixins/observer_mixin.py

class ObserverMixin:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, data):
        for obs in self.observers:
            obs.update(data)
