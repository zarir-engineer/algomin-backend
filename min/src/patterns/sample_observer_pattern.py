####################
# Subject Class: Manages a list of observers and notifies them of state changes.
# ConcreteSubject Class: Implements the Subject interface and maintains the state.
# Observer Class: Defines the update method that concrete observers must implement.
# ConcreteObserverA and ConcreteObserverB Classes: Implement the Observer interface and define specific reactions to state changes.
####################

from abc import ABC, abstractmethod

class Subject(ABC):
    """
    The Subject interface declares a set of methods for managing subscribers.
    """

    @abstractmethod
    def attach(self, observer):
        """Attach an observer to the subject."""
        pass

    @abstractmethod
    def detach(self, observer):
        """Detach an observer from the subject."""
        pass

    @abstractmethod
    def notify(self):
        """Notify all observers about an event."""
        pass

class ConcreteSubject(Subject):
    """
    The ConcreteSubject owns some important state and notifies observers when the state changes.
    """

    _state: int = None
    _observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self):
        for observer in self._observers:
            observer.update(self)

    def set_state(self, state: int):
        self._state = state
        self.notify()

    def get_state(self):
        return self._state

class Observer(ABC):
    """
    The Observer interface declares the update method, used by subjects.
    """

    @abstractmethod
    def update(self, subject):
        pass

class ConcreteObserverA(Observer):
    def update(self, subject):
        if subject.get_state() < 3:
            print("ConcreteObserverA: Reacted to the event")

class ConcreteObserverB(Observer):
    def update(self, subject):
        if subject.get_state() == 0 or subject.get_state() >= 2:
            print("ConcreteObserverB: Reacted to the event")

# Client code
if __name__ == "__main__":
    subject = ConcreteSubject()

    observer_a = ConcreteObserverA()
    subject.attach(observer_a)

    observer_b = ConcreteObserverB()
    subject.attach(observer_b)

    subject.set_state(2)
    subject.set_state(3)
    subject.set_state(0)
