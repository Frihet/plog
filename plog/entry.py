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
Log data abstraction, encoding and decoding.
"""

import logging
import time
import plog
import plog.file2log.syslog

# Log levels
LEVEL_NONE = plog.file2log.syslog.LOG_INFO
LEVEL_DEBUG = plog.file2log.syslog.LOG_DEBUG
LEVEL_INFO = plog.file2log.syslog.LOG_INFO
LEVEL_WARNING = plog.file2log.syslog.LOG_WARNING
LEVEL_ERROR = plog.file2log.syslog.LOG_ERR

# Map from log level string to log level.
NAME_TO_LEVEL = {
    'FINEST': LEVEL_DEBUG, 'FINE': LEVEL_DEBUG, 'DEBUG': LEVEL_DEBUG,
    'INFO': LEVEL_INFO, 'WARN': LEVEL_WARNING, 'WARNING': LEVEL_WARNING,
    'ERROR': LEVEL_ERROR, 'SEVERE': LEVEL_ERROR, '': LEVEL_NONE
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

class Entry(object):
    """
    Common entry format shared between all parsers to allow easy
    conversion and the use of common formatting rules.
    """

    def __init__(self, msg, msg_extra=None, timestamp=None,
                 facility=plog.DEFAULT_FACILITY, level=LEVEL_NONE,
                 extra_values=None, addr=None, name=None):
        """
        Initialize entry, fill in timestamp if not specified.
        """
        # Entry message, log message from syslog / file.
        self.msg = msg
        # Extra message, can be exception from log server etc.
        self.msg_extra = msg_extra
        # Timestamp of entry
        self.timestamp = timestamp
        # Log facility
        self.facility = plog.DEFAULT_FACILITY
        # Level (priority) of entry, can be WARNING etc for format filters.
        self.level = level
        # List of extra values used by a specific log type
        self.extra_values = extra_values
        # IP address of log source
        self.ip_addr = None
        # Name of log source
        self.name = name

        if addr is not None:
            self.ip_addr = addr[0]
        if self.extra_values is None:
            self.extra_values = {}

    @classmethod
    def get_log_type(cls):
        """     
        Return log type.
        """
        return plog.LOG_ENTRY_PLAIN

    @classmethod
    def get_extra_fields(cls):
        """
        Return list of extra fields, implemented by sub-classes.
        """
        return ()

    @classmethod
    def get_signature(cls):
        """
        Return log signature, for plain entries this is nothing.
        """
        return ''

    def _get_timestamp_str(self):
        """
        Format self.timestamp to string for sending over the network,
        sets timestamp to now if not set.
        """
        if self.timestamp is None:
            self.timestamp = time.localtime()
        return time.strftime(plog.LOG_TIME_FORMAT, self.timestamp)

    def _get_timestamp_from_str(self, timestamp_str):
        """
        Get timestamp from string, defaulting to now if parsing fails.
        """
        try:
            timestamp = time.strptime(timestamp_str, plog.LOG_TIME_FORMAT)
        except ValueError:
            logging.info('failed to parse timestamp %s, falling back to now'
                         % (timestamp_str, ))
            timestamp = time.localtime()
        return timestamp

    def _format_syslog(self, name, extra_values):
        """
        Formats message for syslog, no special tricks here.
        """
        return '%s%s|%s|%s|%s|%s|%s' % (
            self.get_signature(), name,
            self._get_timestamp_str(), get_level_str(self.level),
            extra_values, self.msg, self.msg_extra)

    def to_syslog(self, name):
        """
        Encode message for output on syslog including extra
        fields. For complex log data this should be overridden by
        sub-classes.
        """
        extra_values = '|'.join([str(value) for value in self.extra_values])
        return self._format_syslog(name, extra_values)

    def from_syslog(self):
        """
        Decode message delivered from syslog.
        """

class PlogEntry(Entry):
    """
    Base class for plog based messages, adds decoding of plog
    to_syslog messages.
    """

    def from_syslog(self):
        """
        Parse plog style log message.
        """
        extra_fields = self.get_extra_fields()
        num_fields = 5
        if extra_fields:
            num_fields += len(extra_fields)
        else:
            # Add one to get counting right
            num_fields += 1

        # Parse log message
        info = self.msg[5:].split('|', num_fields)
        if num_fields > len(info):
            logging.warning(
                'unable to parse message %s, got %d fields expected max %d'
                % (self.msg, num_fields, info))
            return False

        # Base log data
        self.name = info[0]
        self.msg = info[num_fields - 2]
        self.msg_extra = info[num_fields - 1]
        self.timestamp = self._get_timestamp_from_str(info[1])

        # Log type specific values
        self.extra_values = []
        for pos in xrange(len(extra_fields)):
            field_name, field_type = extra_fields[pos]
            self.extra_values.append(field_type(info[pos+3]))

        return True

class RequestEntry(PlogEntry):
    """
    Request log entry adds extra fields for request status and client
    information.

    Identified by !!RQ signature.
    """

    @classmethod
    def get_log_type(cls):
        """     
        Return log type.
        """
        return plog.LOG_ENTRY_REQUEST

    @classmethod
    def get_extra_fields(cls):
        """
        Return list of extra fields used by request type.
        """
        return (('re_ip', str), ('re_method', str), ('re_user_agent', str),
                ('re_size', int), ('re_status', int), ('re_ms_time', int),
                ('re_uri', str))

    @classmethod
    def get_signature(cls):
        """
        Return log signature.
        """
        return '!!RQ '

class AppserverEntry(PlogEntry):
    """
    Application log entry adds extra fields for traceback and request
    level.

    Identified by !!AS signature.
    """

    @classmethod
    def get_log_type(cls):
        """     
        Return log type.
        """
        return plog.LOG_ENTRY_APPSERVER

    @classmethod
    def get_signature(cls):
        """
        Return log signature.
        """
        return '!!AS '
