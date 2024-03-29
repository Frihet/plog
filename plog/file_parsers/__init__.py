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
Log file parsing routines.
"""

import logging
import cStringIO
import plog.entry

class Parser(object):
    """
    Base class for parser providing a simple interface for feeding
    data in and returning log entries (if data is complete) to logger
    for writing.
    """

    def __init__(self, options):
        """
        Initialize parser setting up a write buffer.
        """
        assert isinstance(options, dict)

        # Write buffer used when feeding the parser with data.
        self.buf = cStringIO.StringIO()
        # Buffer for storing partially parsed log entries
        self.log_buf = cStringIO.StringIO()

    def feed(self, data):
        """
        Feed parser with data, return a list of parsed entries.
        """
        self.buf.write(data)
        self.buf.seek(0)

        return self.parse_buf()

    def parse_buf(self):
        """
        Parse content of the buffer and return a list of parsed entries.
        """
        entries = []

        # Read buffer line by line, remember last position entry was
        # successfully parsed at.
        for line in self.buf:
            try:
                entry = self.parse_line(line)
                if entry is not None:
                    entries.append(entry)
            except:
                # FIXME: Add parser name here
                logging.debug('failed parsing line: %s' % (line, ))

        # Truncate buffer.
        self.buf.reset()
        self.buf.truncate()

        return entries

    def parse_line(self, line):
        """
        Parse single line of data, this should be overridden by
        sub-classes and they can use self.buf_log for storing
        incomplete log entries.
        """
        raise NotImplementedError()

class PlainParser(Parser):
    """
    Plain text parser, does nothing but returning one log entry per
    line of text.
    """

    def parse_line(self, line):
        """
        Parse line, return single log entry.
        """
        return plog.entry.Entry(line)

def get_parser(name, options):
    """
    Get parser class from name.
    """
    if name.lower() == 'apache':
        import plog.file_parsers.apache
        return plog.file_parsers.apache.ApacheParser(options)
    elif name.lower() == 'glassfish':
        import plog.file_parsers.appserver
        return plog.file_parsers.appserver.GlassfishParser(options)
    elif name.lower() == 'tomcat':
        import plog.file_parsers.appserver
        return plog.file_parsers.appserver.TomcatParser(options)
    elif name.lower() == 'plain':
        return PlainParser(options)
    elif name.lower() == 'rails':
        import plog.file_parsers.rails
        return plog.file_parsers.rails.RailsParser(options)
    else:
        raise ValueError('unknown parser named %s' % (name, ))
