import unittest
from unittest.mock import MagicMock

class TestObserverPattern(unittest.TestCase):
    def test_observer_notification(self):
        # Create a concrete subject
        subject = ConcreteSubject()

        # Create mock observers
        observer_a = MagicMock(spec=ConcreteObserverA)
        observer_b = MagicMock(spec=ConcreteObserverB)

        # Attach observers to the subject
        subject.attach(observer_a)
        subject.attach(observer_b)

        # Change the state of the subject
        subject.set_state(2)
        subject.set_state(3)
        subject.set_state(0)

        # Assert that observer_a was notified when state was 2
        observer_a.update.assert_called_with(subject)
        # Assert that observer_b was notified when state was 0
        observer_b.update.assert_called_with(subject)

if __name__ == "__main__":
    unittest.main()
