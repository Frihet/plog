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
import plog.formatters

class AppserverFormatter(plog.formatters.Formatter):
    """
    Formatting of application server events such as Tomcat and
    Glassfish.
    """

    def __init__(self, options):
        """
        Initialize appserver formatter, supported options are:

          * include_traceback, if 1 or yes include traceback in error
            messages.
        """
        plog.formatters.Formatter.__init__(self, options)

        # Regular expression transforming log entries
        self.include_traceback = False

        for option, value in options.iteritems():
            if option == 'include_traceback':
                self.include_traceback = value.lower() in ('1', 'yes')
            else:
                raise ValueError('unsupported option "%s" to AppserverFormatter. Supported options are include_traceback.' % (value, ))

    def format(self, f_obj, entry):
        """
        Format entry with timestamp.
        """
        if self.include_traceback and entry.text_extra:
            extra = ' | %s' % (entry.text_extra, )
        else:
            extra = ''

        text = '!!AS %s | %s | %s%s' % (
            f_obj.name, plog.entry.get_level_str(entry.level),
            entry.text, extra)

        return plog.entry.FormattedEntry(text, entry.level)
