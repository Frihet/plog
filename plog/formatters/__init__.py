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

# Dict with instantiated formatters.
PARSER_INSTANCES = {}

class Formatter(object):
    """
    Base class for transforming parsed log entries into suitable
    syslog messages.
    """

    def __init__(self, options):
        """
        Initialize formatter.
        """
        assert isinstance(options, dict)

    def format(self, f_obj, entry):
        """
        Format single entry returning a text string representation of
        it. Implemented by sub-classes.
        """
        raise NotImplementedError()


def get_formatter(name, options):
    """
    Get formatter from name.
    """
    if name.lower() == 'appserver':
        import plog.formatters.appserver
        return plog.formatters.appserver.AppserverFormatter(options)
    elif name.lower() == 'plain':
        import plog.formatters.plain
        return plog.formatters.plain.PlainFormatter(options)
    else:
        raise ValueError('unknown formatter named %s' % (name, ))

