import logging

from logging import Logger
from typing import Any, Dict, Tuple
from threading import Thread, Event
from abc import ABCMeta, abstractmethod

from netmonitor.notifiers import *


class Monitor(Thread, metaclass=ABCMeta):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__()
        self._stop_event: Event = Event()
        self._args: Tuple[Any, ...] = args
        self._kwargs: Dict[str, Any] = kwargs
        self._delay: int = self.kwargs.get('delay', 300)
        self._logger: Logger = logging.getLogger(self.__class__.__name__)
        self._notifier: Notifier = self.kwargs.get('notifier',
            Terminal(title=self.__class__.__name__))

    def run(self) -> None:
        self._logger.debug(f'Running module...')
        while not self.stopped:
            self._logger.debug('Triggering module run...')
            self._tick()
            self._wait(self._delay)

    def stop(self) -> None:
        self._stop_event.set()

    def _wait(self, timeout: int) -> None:
        self._stop_event.wait(timeout=timeout)

    @abstractmethod
    def _tick(self) -> None:
        raise NotImplementedError
    
    @property
    def stopped(self) -> bool:
        return self._stop_event.is_set()

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def notifier(self) -> Notifier:
        return self._notifier

    @property
    def args(self) -> Tuple[Any, ...]:
        return self._args

    @property
    def kwargs(self) -> Dict[str, Any]:
        return self._kwargs