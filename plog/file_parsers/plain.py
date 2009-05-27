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

import plog.entry, plog.file_parsers.parsers

class PlainParser(plog.file_parsers.Parser):
    """
    Plain text parser, does nothing but returning one log entry per
    line of text.
    """

    def parse_line(self, line):
        """
        Parse line, return single log entry.
        """
        return plog.entry.FileEntry(line)