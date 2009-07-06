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
Rails log-file parser.
"""

import re
import time
import cStringIO
import plog
import plog.entry
import plog.file_parsers

class RailsParser(plog.file_parsers.Parser):
    """
    Parser for Rails production log files, outputs request log files
    and not appserver as one might think as rails log files include
    full request information.
    """

    # Request line regular expression for extracting ip, time (date)
    # and http method
    RE_REQUEST = re.compile(
        'Processing [^+\(]+\(for ([^ ]+) at ([^\)]+)\) \[([^\]]+).')

    # Status line regular expression for extracting time (ms), http status
    # and requested URI.
    RE_STATUS = re.compile(
        'Completed in ([0-9]+)ms[^|]+\| ([0-9]+)[^\[]+\[([^\]]+)')

    def __init__(self, options):
        """
        Initialize parser state.
        """
        plog.file_parsers.Parser.__init__(self, options)

        # Parser flag, in message parsing.
        self.in_message = False
        # Boolean flag set if last line was a newline.
        self.last_is_newline = False
        # Parser state detecting end of entry.
        self.has_rendered_or_completed = False
        # Parser message buffer.
        self.msg_buf = cStringIO.StringIO()

    def parse_line(self, line):
        """
        Parse line, return a an entry or None.
        """
        entry = None

        if self.in_message:
            self.msg_buf.write(line)

            if line == '\n':
                if self.last_is_newline and self.has_rendered_or_completed:
                    entry = self._create_entry(self.msg_buf.getvalue())
                    self.msg_buf.reset()
                    self.msg_buf.truncate()
                    self.has_rendered_or_completed = False

                # Toggle last_is_newline, if it was previously set a
                # new entry has begun it should be enabled or else it
                # should be flagged.
                self.last_is_newline = not self.last_is_newline
            else:
                if self.last_is_newline and line.startswith('Rendering'):
                    self.has_rendered_or_completed = True
                elif line.startswith('Completed'):
                    self.has_rendered_or_completed = True
                self.last_is_newline = False

        elif line == '\n':
            self.in_message = self.last_is_newline
            self.last_is_newline = True
        else:
            self.last_is_newline = False

        return entry

    def _create_entry(self, msg):
        """
        Create entry for message text, the entry is formatted starting
        with 2 newlines, 2 ending newlines.

        The first line is request information, second is parameters if
        errors occur a blank line is presented and then a traceback
        printed followed by another newline and rails status. The
        status is the last line of the log entry.
        """
        if not msg:
            return

        # Drop starting and ending newlines
        msg_full = msg[0:-3]
        msg_lines = msg.split('\n')
        
        # First line is request info, in form:
        #
        #   Processing ControllerName#action
        #   (for 0.0.0.0 at 000-00-00 00:00:00) [GET]
        #
        msg = msg_lines[0]
        try:
            ip_addr, timestamp, method = self.RE_REQUEST.search(msg).groups()
        except AttributeError:
            logging.debug('failed to parse rails request line: %s' % (msg, ))
            return None
        except ValueError:
            logging.debug('failed to parse rails request line: %s' % (msg, ))
            return None

        # Convert string timestamp into datetime
        timestamp = time.strptime(timestamp, plog.TIME_FORMAT)

        # User agent and size is empty as it is not logged
        size = 0
        user_agent = plog.USER_AGENT_UNKNOWN
        
        # If a blank line is found, an error occurred and the
        # traceback is placed between the first line after the blank
        # until two lines before the end
        traceback_start = msg_full.find('\n\n')
        if traceback_start != -1:
            traceback_end = msg_full.rfind('\n\n')
            msg_extra = msg_full[traceback_start:traceback_end]
        else:
            msg_extra = None

        # Last line is final status, if a blank line was found assume
        # something went wrong or if now completed line

        status_start = msg_full.rfind('\nCompleted in')
        status_end = msg_full.find('\n', status_start + 1)
        status = msg_full[status_start:status_end]

        if traceback_start == -1 and status:
            # Status line is in format:
            #
            #   Completed in 102ms (View: 15, DB: 52) | 200 OK [http://url]
            #
            try:
                ms_time, status, uri = self.RE_STATUS.search(status).groups()
                status = int(status)
            except:
                print status
                raise
        else:
            ms_time = 0
            status = 500
            uri = plog.URI_ERROR

        # Map HTTP code into level
        if status in plog.HTTP_CODES_OK:
            level = plog.entry.LEVEL_INFO
        elif status in plog.HTTP_CODES_WARNING:
            level = plog.entry.LEVEL_WARNING
        else:
            level = plog.entry.LEVEL_ERROR

        return plog.entry.RequestEntry(
            msg, msg_extra, timestamp, plog.DEFAULT_FACILITY, level,
            [ip_addr, method, user_agent, size, status, ms_time, uri]
            )
