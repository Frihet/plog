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
Apache log-file parser.
"""

import re, time
import plog, plog.entry, plog.file_parsers

class ApacheParser(plog.file_parsers.Parser):
    """
    Parser for Apache common log files, outputs request log files.
    """

    # Access entries

    # Regular expression parsing access log entries
    RE_ACCESS = re.compile('^([0-9\.]+) - - \[([^\]]+)\] "([^ ]+) ([^ ]+) ([^"]+)" ([0-9-]+) ([0-9-]+) "([^"]+)?" "([^"]+)"')

    # Time format used for access entries
    TIME_FORMAT = '%d/%b/%Y:%H:%M:%S'

    # Fields for access regexp
    FIELD_IP = 0
    FIELD_DATETIME = 1
    FIELD_METHOD = 2
    FIELD_URI = 3
    FIELD_PROTO = 4
    FIELD_STATUS = 5
    FIELD_SIZE = 6
    FIELD_REQ_TIME = 7
    FIELD_UA = 8

    # Error entries

    # Regular expression parsing error log entries
    RE_ERROR = re.compile('^\[([^\]]+)\] \[([^\]]+)\] \[client ([0-9\.]+)\] (.*)')

    # Time format used for error entries
    ERROR_TIME_FORMAT = '%a %b %d %H:%M:%S %Y'

    # Fields for error regexp
    FIELD_ERROR_DATETIME = 0
    FIELD_ERROR_LEVEL = 1
    FIELD_ERROR_IP = 2
    FIELD_ERROR_MSG = 3

    def __init__(self, options):
        """
        Initialize parser state.
        """
        plog.file_parsers.Parser.__init__(self, options)

    def parse_line(self, line):
        """
        Parse line, return a an entry or None.
        """
        entry = None

        access = ApacheParser.RE_ACCESS.search(line)
        if access is not None:
            entry = self._create_access_entry(access.groups())
        else:
            error = ApacheParser.RE_ERROR.search(line)
            if error is not None:
                entry = self._create_error_entry(error.groups())
            else:
                print "FAILED"
                print line

        return entry

    def _create_access_entry(self, access):
        """
        Create log entry for access request.
        """
        # FIXME: Handle timezone
        time_str = access[ApacheParser.FIELD_DATETIME].split()[0]
        timestamp = time.strptime(time_str, ApacheParser.TIME_FORMAT)

        # FIXME: Add utility value_form_str or similar that falls back
        #        to default value if parsing fails.
        try:
            size = int(access[ApacheParser.FIELD_SIZE])
        except ValueError:
            size = 0
        try:
            status = int(access[ApacheParser.FIELD_STATUS])
        except ValueError:
            status = 200

        # FIXME: Support request time parsing, can be specified in
        #        usec and what other formats?
        ms_time = 0

        # FIXME: Move to common code Map HTTP code into level
        if status in plog.HTTP_CODES_OK:
            level = plog.entry.LEVEL_INFO
        elif status in plog.HTTP_CODES_WARNING:
            level = plog.entry.LEVEL_WARNING
        else:
            level = plog.entry.LEVEL_ERROR

        return plog.entry.RequestEntry(
            access[ApacheParser.FIELD_URI], None, timestamp,
            plog.DEFAULT_FACILITY, level,
            [access[ApacheParser.FIELD_IP], access[ApacheParser.FIELD_METHOD],
             access[ApacheParser.FIELD_UA], size, status, ms_time,
             access[ApacheParser.FIELD_URI]])

    def _create_error_entry(self, error):
        """
        Create log entry for error request.
        """
        # FIXME: Handle timezone
        time_str = error[ApacheParser.FIELD_ERROR_DATETIME]
        timestamp = time.strptime(time_str, ApacheParser.ERROR_TIME_FORMAT)

        size = 0
        status = 503
        ms_time = 0
        method = ''
        level = plog.entry.LEVEL_ERROR

        # FIXME: Support detecting more messages from apache

        msg = error[ApacheParser.FIELD_ERROR_MSG]
        if msg.startswith('File does not exist:'):
            status = 404
            level = plog.entry.LEVEL_WARNING

        return plog.entry.RequestEntry(
            msg, None, timestamp,
            plog.DEFAULT_FACILITY, level,
            [error[ApacheParser.FIELD_ERROR_IP], plog.USER_AGENT_UNKNOWN,
             method, size, status, ms_time, ''])
        
