from abc import ABC
from agilepy.utils.Observer import Observer

class Observable(ABC):
    """
    The Observable interface declares a set of methods for managing subscribers.
    """
    def __init__(self):
        self._observers = {}

    def attach(self, observer: Observer, type: str) -> None:
        if type not in self._observers:
            self._observers[type] = []
        self._observers[type].append(observer)

    def detach(self, observer: Observer, type: str) -> None:
        if type in self._observers:
            self._observers[type].remove(observer)

    def notify(self, type, newstate) -> None:

        if type in self._observers:
            for o in self._observers[type]:
                o.update(type, newstate)
