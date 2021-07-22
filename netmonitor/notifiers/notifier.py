from abc import ABCMeta, abstractmethod


class Notifier(metaclass=ABCMeta):

    def __init__(self, title: str):
        self._title = title

    @abstractmethod
    def notify(self, message: str) -> bool:
        raise NotImplementedError

    @property
    def title(self) -> str:
        return self._title