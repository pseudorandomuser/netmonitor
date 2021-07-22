import sys
import json
import logging

from logging import Logger
from typing import Any, Dict, List

from netmonitor import monitors
from netmonitor.monitors.monitor import Monitor

from netmonitor.notifiers import *


def main(*args: Any, **kwargs: Any) -> bool:

    logger: Logger = logging.getLogger(__name__)
    logger.debug('Starting all modules...')

    interrupt_count: int = 0
    monitor_threads: List[Monitor] = []

    pushover_user_key = kwargs.get('pushover_user_key')
    pushover_token_key = kwargs.get('pushover_token_key')
    
    for _, attribute in monitors.__dict__.items():
        if isinstance(attribute, type) and issubclass(attribute, Monitor) and not issubclass(Monitor, attribute):
            logger.debug(f'Starting module: "{attribute.__name__}"...')
            monitor_arguments: Dict[str, Any] = kwargs.get(f'{attribute.__module__}.{attribute.__name__}', {})
            monitor_title: str = f'Network Monitor ({attribute.__name__})'
            if pushover_user_key and pushover_token_key:
                monitor_notifier: Notifier = Pushover(user=pushover_user_key, token=pushover_token_key, title=monitor_title)
            else:
                monitor_notifier = Terminal(title=monitor_title)
            current_monitor: Monitor = attribute(notifier=monitor_notifier, **monitor_arguments) # type: ignore
            monitor_threads.append(current_monitor)
            current_monitor.start()

    while True:
        try:
            logger.debug('Waiting for monitor threads to exit...')
            for current_monitor in monitor_threads:
                current_monitor.join()
            break
        except KeyboardInterrupt as exception:
            if interrupt_count >= 2:
                raise exception
            interrupt_count += 1
            logger.info('Stopping all monitors...')
            for current_monitor in monitor_threads:
                current_monitor.stop()

    return True


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with open('config.json', 'r') as config_handle:
        config_dict: Dict[str, Any] = json.load(config_handle)
        sys.exit(not main(**config_dict))