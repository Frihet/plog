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
System log to database writer module, includes the Log2DbDaemon
application.
"""

import socket, re
import plog, plog.daemon, plog.entry, plog.log2db.writer

# Rules identifying log message
CLASSIFY_RULES = (
    (re.compile('^!!AS '), plog.entry.LogEntryAppserver),
    (re.compile('^!!RQ '), plog.entry.LogEntryRequest),
    (re.compile('^.'), plog.entry.LogEntryPlain)
    )

class Log2DbDaemon(plog.daemon.Daemon):
    """
    Log2Db daemon application, reads syslog events from the network,
    classifies, parses and writes it to a database.
    """

    def __init__(self):
        """
        Initialize Log2DbDaemon.
        """
        plog.daemon.Daemon.__init__(self, 'log2db')

        # Network socket
        self._socket = None
        # Writer thread
        self._db_writer = None

    def _daemon_main(self):
        """
        Daemon main, recv events and add them to the writer.
        """
        # Initialize network listening
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        address = self._config.get('log2db', 'bind_address', '0.0.0.0')
        port = int(self._config.get('log2db', 'bind_port', '514'))

	self._socket.bind((address, port))

        # FIXME: Support other database writer types

        # Create and start writer
        self._writer = plog.log2db.writer.MySQLDBWriter(self._config)
        self._writer.start()

        while self._do_run():
            # FIXME: Check for configuration re-loading
            data, addr = self._recv_event()
            if data is not None:
                # Create event from syslog traffic
                event = self._construct_event(data, addr)
                self._writer.add(event)

        self._writer.stop()

    def _recv_event(self):
        """
        Get syslog event from the network.
        """
        try:
            data, addr = self._socket.recvfrom(plog.READ_LOG_MAX)
        except socket.error:
            # FIXME: Debug logging
            data = addr = None

        return (data, addr)

    def _construct_event(self, data, addr):
        """
        Construct event from syslog data.
        """
        message =  self._decode_syslog(data)
        if message is not None:
            facility, priority, data = message
            event_class = self._classify_event(data, addr)
            return event_class(data, addr, facility, priority)

    def _decode_syslog(self, data):
        """
        Decode syslog format <X>message\000 returning a three element tuple
        including (facility, priority, message)
        """
        # Make sure log starts with < >
        if data[0] != '<':
            return None
        log_start = data.find('>')
        if log_start == -1:
            return None

        # Decode priority
        try:
            facility_priority = int(data[1:log_start])
            facility = (facility_priority & 0xf8) >> 3
            priority = facility_priority & 0x07
        except ValueError:
            return None

        if data[-1] == '\000':
            data = data[log_start+1:-1]
        else:
            data = data[log_start+1:]

        return (facility, priority, data)

    def _classify_event(self, data, addr):
        """
        Run classification rules against log message return event
        class to be used for constructing log entry.
        """
        for rule, event_class in CLASSIFY_RULES:
            if rule.match(data):
                return event_class
        return plog.entry.LogEntryPlain

def main():
    """
    Main route, entry point for application.
    """
    application = Log2DbDaemon()
    application.main()

if __name__ == '__main__':
    main()
