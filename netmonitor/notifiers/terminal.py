import logging

from logging import Logger
from netmonitor.notifiers.notifier import Notifier


class Terminal(Notifier):

    def __init__(self, title: str) -> None:
        super().__init__(title=title)
        self._logger: Logger = logging.getLogger(self.__class__.__name__)

    def notify(self, message: str) -> bool:
        self._logger.info(f'Notifier: Title: {self.title}, '
            f'Message: {message}')
        return True