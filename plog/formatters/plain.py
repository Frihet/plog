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

import time, re
import plog.formatters

class PlainFormatter(plog.formatters.Formatter):
    """
    Plain text formatter, outputs entry with timestamp.
    """

    def __init__(self, options):
        """
        Initialize plain formatter, supported options are:

          * transform, regular expression transforming the
            entries. Example format is \1 FOO|(.*) BAR
        """
        plog.formatters.Formatter.__init__(self, options)

        # Regular expression transforming log entries
        self.transform_re = None
        self.transform_str = None

        for option, value in options.iteritems():
            if option == 'transform':
                # FIXME: Error handling in parsing
                self.transform_str, self.transform_re = value.split('|', 1)
                self.transform_re = re.compile(self.transform_re)
            else:
                raise ValueError('unsupported option "%s" to PlainFormatter. Supported options are transform.')

    def format(self, f_obj, entry):
        """
        Format entry with timestamp.
        """
        # Transform entry if requested, can be used for removing
        # redundant information etc.
        if self.transform_re is None:
            text = entry.text
        else:
            text = self.transform_re.sub(self.transform_str, entry.text)

        return plog.entry.FormattedEntry('%s - %s' % (f_obj.name, text))
