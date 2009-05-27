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

import re, cStringIO
import plog.entry, plog.file_parsers

class TomcatParser(plog.file_parsers.Parser):
    """
    Parser for tomcat catalina.out style log files. As the rules for
    such log files are not very strict this parser is not 100%
    accurate.
    """

    # Regular expression for matching start of a log message
    RE_LINE = re.compile('(DEBUG|INFO|WARNING|ERROR|SEVERE)[ :]')

    def __init__(self, options):
        """
        Initialize parser state.
        """
        file2log.parsers.Parser.__init__(self, options)

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

        fields = msg.split('\n', 1)

        # Get text and possibly traceback
        text = fields[0]
        if len(fields) > 1 and fields[1]:
            text_extra = fields[1]
        else:
            text_extra = None

        # Get level, continue parsing "severe" enough
        level_name = TomcatParser.RE_LINE.search(msg).group(1)
        level = file2log.entry.get_level(level_name)

        # FIXME: Support parsing the timestamp
        timestamp = None

        return plog.entry.FileEntry(text, text_extra, timestamp, level)

