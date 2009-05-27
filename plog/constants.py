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

# Exit value returned when printing usage information.
EXIT_USAGE = 1
# Time in seconds to sleep between stat sweeps in the reader
READ_INTERVAL = 0.01
# Maximum amount of data to read in a single iteration
READ_MAX = 8192
# Maximum log event size
READ_LOG_MAX = 32768
# In config file option for the datbase section
CFG_SECT_DATABASE = 'database'
# In config file option for setting file path
CFG_OPT_PATH = 'path'
# In config file option for setting parser
CFG_OPT_PARSER = 'parser'
# In config file option for setting formatter
CFG_OPT_FORMATTER = 'formatter'
# Default parser type
DEFAULT_PARSER = 'plain'
# Default formatter type
DEFAULT_FORMATTER = 'plain'
# Default logging facility, 1 is LOG_USER
DEFAULT_FACILITY = 3
# Default logging priority, 6 is LOG_INFO
DEFAULT_PRIORITY = 4
# Default path to configuration file
PATH_CONFIG = 'plog.cfg'
