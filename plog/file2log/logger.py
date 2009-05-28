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

    def log(self, f_entries):
        """
        Write formatted entry to syslog.
        """
        for f_entry in f_entries:
            self._log_until_size_ok(f_entry)

    def _log_until_size_ok(self, f_entry):
        """
        Write formatted entry to syslog, re-try until message fits
        allowed size.
        """
        not_sent = True
        text = f_entry.text
        while not_sent and len(text) > 1:
            try:
                self.syslog.log(text, facility=f_entry.facility,
                                priority=f_entry.priority)
                not_sent = False
            except socket.error, exc:
                if exc.errno == errno.EMSGSIZE:
                    text = text[:len(text) / 2]
                else:
                    raise
