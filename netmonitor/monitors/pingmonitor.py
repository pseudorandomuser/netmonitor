import re
import socket
import shutil
import subprocess

from datetime import datetime
from typing import Optional, Sequence, Tuple, Dict, List, Any

from netmonitor.monitors.monitor import Monitor


class PingMonitor(Monitor):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._host_states: Dict[str, bool] = {}
        self._ping_bin: Optional[str] = shutil.which('ping')
        self._host_list: List[str] = self.kwargs.get('host_list', [])

    def _ping(
            self, host_addr: str, 
            attempts: int = 1, 
            timeout: int = 1
    ) -> Tuple[bool, float]:
        ping_proc: subprocess.Popen = subprocess.Popen([
            self._ping_bin if self._ping_bin else '/sbin/ping', 
            '-c', str(attempts),
            '-t', str(timeout), 
            host_addr
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ping_output: str = ping_proc.communicate()[0].decode('UTF-8')
        ping_search: Optional[re.Match] = re.search('=(.*) ms', ping_output)
        ping_latency: float = 0
        if ping_search is not None:
            ping_groups: Sequence[Any] = ping_search.groups()
            if len(ping_groups) >= 1:
                ping_latency = float(ping_groups[0])
        return (ping_proc.returncode == 0, ping_latency)

    def _tick(self) -> None:
        for host in self._host_list:
            if self.stopped:
                break
            current_ping: float
            current_state: bool
            current_date = datetime.now()
            hostname: str = socket.getfqdn(host)
            timestr: str = current_date.strftime('%A, %d. %B %Y at %H:%M:%S')
            previous_state: Optional[bool] = self._host_states.get(host)
            current_state, current_ping = self._ping(host)
            if previous_state != current_state:
                status: str = f'up, ping {current_ping} ms' \
                    if current_state else 'down'
                self.notifier.notify(f'Host "{hostname}" ({host}) '
                    f'is {status}, {timestr}.')
            self._host_states[host] = current_state