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

import time
import plog, plog.file2log.syslog

# Log levels
LEVEL_NONE = plog.file2log.syslog.LOG_INFO
LEVEL_DEBUG = plog.file2log.syslog.LOG_DEBUG
LEVEL_INFO = plog.file2log.syslog.LOG_INFO
LEVEL_WARNING = plog.file2log.syslog.LOG_WARNING
LEVEL_ERROR = plog.file2log.syslog.LOG_ERR

# Map from log level string to log level.
NAME_TO_LEVEL = {
    'FINEST': LEVEL_DEBUG, 'FINE': LEVEL_DEBUG, 'DEBUG': LEVEL_DEBUG,
    'INFO': LEVEL_INFO, 'WARNING': LEVEL_WARNING, 'ERROR': LEVEL_ERROR,
    'SEVERE': LEVEL_ERROR, '': LEVEL_NONE
    }

# Map from log level to string.
LEVEL_TO_NAME = {
    LEVEL_DEBUG: 'DEBUG', LEVEL_INFO: 'INFO',
    LEVEL_WARNING: 'WARNING', LEVEL_ERROR: 'ERROR',
    LEVEL_NONE: 'UNKNOWN'
    }

def get_level(level_str):
    """
    Get log level from string representation.
    """
    return NAME_TO_LEVEL.get(level_str.upper(), LEVEL_NONE)

def get_level_str(level):
    """
    Get log level string from level.
    """
    return LEVEL_TO_NAME.get(level, 'UNKNOWN')

class FileEntry(object):
    """
    Common file entry format shared between all parsers allowing the
    formatting rules to apply.
    """

    def __init__(self, text, text_extra=None, timestamp=None, level=LEVEL_NONE):
        """
        Initialize entry, fill in timestamp if not specified.
        """
        # Entry text, for plain text files this is everything.
        self.text = text
        # Extra text, can be an exception in application server files.
        self.text_extra = text_extra
        # Timestamp of entry
        self.timestamp = timestamp
        # Level of entry, can be WARNING etc for format filters.
        self.level = level

        # Fill
        if self.timestamp is None:
            self.timestamp = time.localtime()

class FormattedEntry(object):
    """
    Formatted file entry including destination information such as
    facility.
    """

    def __init__(self, text,
                 priority=plog.DEFAULT_PRIORITY,
                 facility=plog.DEFAULT_FACILITY):
        """
        Initialize formatted entry.
        """
        # Text of formatted entry
        self.text = text
        # Priority to send formatted entry as.
        self.priority = priority
        # Facility to send formatted entry to.
        self.facility = facility

class LogEntry(object):
    """
    Entry base class for log entries received from the network.
    """

    def __init__(self, data, addr, facility, priority,
                 log_type=plog.LOG_ENTRY_PLAIN):
        """
        Initialize log entry.
        """
        # Type of log entry
        self.log_type = log_type
        # Time when event occurred, defaults to local time now
        self.log_time = None
        # IP address of the source
        self.ip = addr[0]
        # Log facility
        self.facility = facility
        # Log priority
        self.priority = priority
        # Event text, available in the base log table
        self.text = None
        # Event extra text, available in the base log table
        self.extra_text = None
        
        # Name of the log extra class
        self.extra_class = None
        # Parameters when constructing the log extra class
        self.extra_params = None

class LogEntryPlain(LogEntry):
    """
    Plain log entries received from the network.
    """

    def __init__(self, data, addr, facility, priority):
        """
        Initialize plain log entry, only sets the event.text
        """
        LogEntry.__init__(self, data, addr, facility, priority)

        # Set the complete log message as the text
        self.text = data

class LogEntryFile2Log(LogEntry):
    """
    Base class for all file2log based log events.
    """

class LogEntryAppserver(LogEntryFile2Log):
    """
    Application server log entries, identified by !!AS
    """

    def __init__(self, data, addr, facility, priority):
        """
        Initialize plain log entry, only sets the event.text
        """
        LogEntry.__init__(self, data, addr, facility, priority,
                          plog.LOG_ENTRY_APPSERVER)

        # Parse log message
        info = data[5:].split(' | ', 3)
        if len(info) < 3:
            # FIXME: Handle invalid message
            pass
        elif len(info) == 3:
            info.append(None)

        # Base log data
        self.text = info[2]
        self.extra_text = info[3]

        # Appserver specific data
        self.extra_class = plog.orm.LogExtraAppserver
        # FIXME: Convert as_level into integer value
        self.extra_params = {'as_name': info[0], 'as_level': info[1]}

class LogEntryRequest(LogEntryFile2Log):
    """
    Request log entries, identified by !!RQ
    """

    def __init__(self, data, addr, facility, priority):
        """
        Initialize plain log entry, only sets the event.text
        """
        LogEntry.__init__(self, data, addr, facility, priority,
                          plog.LOG_ENTRY_REQUEST)

        # FIXME: Implement LogEntryRequest parsing
        raise NotImplementedError()

