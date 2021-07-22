import logging
import requests

from netmonitor.notifiers.terminal import Terminal


class Pushover(Terminal):

    def __init__(self, user: str, token: str, title: str) -> None:
        super().__init__(title=title)
        self._user = user
        self._token = token
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.debug(f'Created Pushover notifier "{title}" with app token "{token}" and user token "{user}"')

    def notify(self, message: str) -> bool:
        super().notify(message)
        pushover_data = {
            'user': self._user,
            'token': self._token,
            'message': message,
            'title': self.title
        }
        pushover_request = requests.post('https://api.pushover.net/1/messages.json', data=pushover_data)
        return pushover_request.status_code == 200