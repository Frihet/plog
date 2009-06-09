# This file is part of plog.
#
# plog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.
#
# plog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with plog.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Log output wrapper, sends log entries to setup logger.
"""

import errno, socket
import plog.file2log.syslog

class Logger(object):
    """
    Syslog output sending formatted log records to the current syslog
    server.
    """

    def __init__(self, config):
        """
        Initialize logger.
        """
        host = config.get('file2log', 'syslog_host', '127.0.0.1')
        port = int(config.get('file2log', 'syslog_port', '541'))

        if host.lower() in ('localhost', '127.0.0.1') and port == 541:
            self.syslog = plog.file2log.syslog.syslog_client()
        else:
            self.syslog = plog.file2log.syslog.syslog_client((host, port))

    def log(self, name, entries):
        """
        Write formatted entry to syslog.
        """
        for entry in entries:
            msg = entry.to_syslog(name)
            self._log_until_size_ok(entry.facility, entry.level, msg)

    def _log_until_size_ok(self, facility, priority, msg):
        """
        Write formatted entry to syslog, re-try until message fits
        allowed size.
        """
        not_sent = True
        while not_sent and len(msg) > 1:
            try:
                self.syslog.log(msg, facility=facility, priority=priority)
                not_sent = False
            except socket.error, exc:
                if exc.errno == errno.EMSGSIZE:
                    msg = msg[:len(msg) / 2]
                else:
                    raise
