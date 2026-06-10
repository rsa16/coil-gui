from typing import Any, Callable, List, Generic, TypeVar, Dict
from contextlib import contextmanager

T = TypeVar("T")

_batch_depth = 0
_pending_notifications: Dict[Callable[[Any], None], Any] = {}

@contextmanager
def batch_updates():
    global _batch_depth
    _batch_depth += 1
    try:
        yield
    finally:
        _batch_depth -= 1
        if _batch_depth == 0:
            pending = list(_pending_notifications.items())
            _pending_notifications.clear()
            for observer, value in pending:
                observer(value)

class Observable(Generic[T]):
    def __init__(self, value: T):
        self._value = value
        self._observers: List[Callable[[T], None]] = []

    def get(self) -> T:
        return self._value

    def set(self, value: T):
        if self._value != value:
            self._value = value
            self._notify()

    def subscribe(self, observer: Callable[[T], None]):
        if observer not in self._observers:
            self._observers.append(observer)
        # Initial notification
        observer(self._value)

    def unsubscribe(self, observer: Callable[[T], None]):
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self):
        for observer in self._observers:
            if _batch_depth > 0:
                _pending_notifications[observer] = self._value
            else:
                observer(self._value)

    @property
    def value(self) -> T:
        return self.get()

    @value.setter
    def value(self, val: T):
        self.set(val)

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return f"Observable({repr(self._value)})"