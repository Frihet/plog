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

import cStringIO

# Dict with instantiated parsers.
PARSER_INSTANCES = {}

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
            entry = self.parse_line(line)
            if entry:
                entries.append(entry)

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

def get_parser(name, options):
    """
    Get parser class from name.
    """
    if name.lower() == 'glassfish':
        import plog.file_parsers.glassfish
        return plog.file_parsers.glassfish.GlassfishParser(options)
    elif name.lower() == 'tomcat':
        import plog.file_parsers.tomcat
        return plog.file_parsers.tomcat.TomcatParser(options)
    elif name.lower() == 'plain':
        import plog.file_parsers.plain
        return plog.file_parsers.plain.PlainParser(options)
    else:
        raise ValueError('unknown parser named %s' % (name, ))
