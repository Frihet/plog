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
Application server log file parsing for glassfish, tomcat etc.
"""

import logging, re, time, cStringIO
import plog, plog.entry, plog.file_parsers

class GlassfishParser(plog.file_parsers.Parser):
    """
    Parser for Glassfish log files.
    """

    # Field number specifications
    FIELD_TIME = 1
    FIELD_LEVEL = 2
    FIELD_TEXT = 4
    FIELD_TEXT_EXTRA = 6

    # Time format in glassfish logs, 2009-05-15T00:00:00.609+0200 but
    # dropping the timezone and sub second granularity.
    LOG_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'

    def __init__(self, options):
        """
        Initialize parser state.
        """
        plog.file_parsers.Parser.__init__(self, options)

        # Parser flag, in message parsing
        self.in_message = False
        # Parser message buffer.
        self.msg_buf = cStringIO.StringIO()

    def parse_line(self, line):
        """
        Parse line, return a an entry or None.
        """
        entry = None

        if self.in_message:
            self.msg_buf.write(line)
            # Parse log data
            if line.endswith(']\n'):
                self.in_message = False
                entry = self._create_entry(self.msg_buf.getvalue())
                self.msg_buf = cStringIO.StringIO()

        elif line.startswith('['):
            if line.endswith(']\n'):
                # Single line message
                entry = self._create_entry(line)
            else:
                # Multi line message
                self.in_message = True
                self.msg_buf = cStringIO.StringIO()
                self.msg_buf.write(line)

        return entry

    def _create_entry(self, msg):
        """
        Create entry for message text.
        """
        if not msg:
            return

        # Get message into fields
        fields = msg.split('|')

        level = plog.entry.get_level(fields[GlassfishParser.FIELD_LEVEL])

        # FIXME: Parse timestamp 2009-05-15T00:00:00.609+0200
        try:
            # Get timestamp removing sub second and timezone info.
            timestamp_str = fields[GlassfishParser.FIELD_TIME]
            timestamp_str = timestamp_str[:timestamp_str.rfind('.')]
            timestamp = time.strptime(
                timestamp_str, GlassfishParser.LOG_TIME_FORMAT)
        except ValueError:
            logging.debug('unable to parse glassfish timestamp %s'
                          % (timestamp_str, ))
            timestamp = None

        return plog.entry.AppserverEntry(
            fields[GlassfishParser.FIELD_TEXT],
            fields[GlassfishParser.FIELD_TEXT_EXTRA],
            timestamp, plog.DEFAULT_FACILITY, level)

class TomcatParser(plog.file_parsers.Parser):
    """
    Parser for tomcat catalina.out style log files. As the rules for
    such log files are not very strict this parser is not 100%
    accurate.
    """

    # Regular expression for matching start of a log message
    RE_LINE = re.compile('(DEBUG|INFO|WARN|WARNING|ERROR|SEVERE)[ :]')

    FIELD_MESSAGE = 0
    FIELD_TRACEBACK = 1

    def __init__(self, options):
        """
        Initialize parser state.
        """
        plog.file_parsers.Parser.__init__(self, options)

        # Parser flag, in message parsing
        self.in_message = False
        # Parser message buffer.
        self.msg_buf = cStringIO.StringIO()        

    def parse_line(self, line):
        """
        Parse line, return log entry if a complete entry is found.
        """
        entry = None

        if self.in_message:
            # Parse log data
            if TomcatParser.RE_LINE.search(line):
                self.in_message = False
                entry = self._create_entry(self.msg_buf.getvalue())
                self.msg_buf = cStringIO.StringIO()
            self.msg_buf.write(line)

        elif TomcatParser.RE_LINE.search(line):
            self.in_message = True
            self.msg_buf = cStringIO.StringIO()
            self.msg_buf.write(line)

        return entry

    def _create_entry(self, msg):
        """
        Finish parsing of message.
        """
        if not msg:
            return None
        info = msg.split('\n', 1)

        # Get text and possibly traceback
        msg = info[TomcatParser.FIELD_MESSAGE]
        if ( len(info) > TomcatParser.FIELD_TRACEBACK
             and info[TomcatParser.FIELD_TRACEBACK] ):
            msg_extra = info[TomcatParser.FIELD_TRACEBACK]
        else:
            msg_extra = None

        # Get level, continue parsing "severe" enough
        level_name = TomcatParser.RE_LINE.search(msg).group(1)
        level = plog.entry.get_level(level_name)

        # FIXME: Support user defined timstamp formats.
        timestamp_str = ''
        try:
            timestamp = time.strptime(timestamp_str, plog.LOG_TIME_FORMAT)
        except ValueError:
            logging.debug('unable to parse tomcat timestamp %s'
                          % (timestamp_str, ))
            timestamp = None

        return plog.entry.AppserverEntry(
            msg, msg_extra, timestamp, plog.DEFAULT_FACILITY, level)

