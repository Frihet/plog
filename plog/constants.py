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
Plog constants, shared settings between all plog modules.
"""

# Current version of plog
VERSION = '0.1.0'

# Exit value returned when printing usage information.
EXIT_USAGE = 1
# Time in seconds to sleep between stat sweeps in the reader
READ_INTERVAL = 0.01
# Time in seconds to sleep between sending log entries.
SYSLOG_INTERVAL = 0.0001
# Maximum amount of data to read in a single iteration
READ_MAX = 8192
# Maximum log event size
READ_LOG_MAX = 32768

# Default parser type
DEFAULT_PARSER = 'plain'
# Default logging facility, 1 is LOG_USER
DEFAULT_FACILITY = 3
# Default logging priority, 6 is LOG_INFO
DEFAULT_PRIORITY = 4
# Default path to configuration file
PATH_CONFIG = '/etc/plog.cfg'

# Plog main configuration
CFG_SECT_GLOBAL = 'plog'
# In config file option for the logging section
CFG_SECT_LOGGING = 'logging'
# In config file option for the database section
CFG_SECT_DATABASE = 'database'
# In config file option for setting file path
CFG_OPT_PATH = 'path'
# In config file option for pid file directory
CFG_OPT_PID_PATH = '/var/run'
# In config file option for setting parser
CFG_OPT_PARSER = 'parser'
# In config file option for setting log level
CFG_OPT_LOG_LEVEL = 'log_level'
# Default value for log level option
CFG_OPT_LOG_LEVEL_DEFAULT = 'WARNING'
# In config file option for setting log path
CFG_OPT_LOG_PATH = 'path'
# Default value for log path option
CFG_OPT_LOG_PATH_DEFAULT = '/var/log/plog'
# In config file option for daemonizing
CFG_OPT_DAEMONIZE = 'daemonize'
# User to run as
CFG_OPT_USER = 'user'
# Group to run as
CFG_OPT_GROUP = 'group'

# In environment option for configuration file position
ENV_OPT_CONFIG = 'PLOG_CONFIG'

# log2db database connect retry interval
LOG2DB_RETRY_INTERVAL = 5.0

# Log types, these types need to reflect correct values in the database
LOG_ENTRY_PLAIN = 0
LOG_ENTRY_REQUEST = 1
LOG_ENTRY_APPSERVER = 2

# Log parsing, HTTP codes that should be considered ok.
HTTP_CODES_OK = (200, 302)
# Log parsing, HTTP codes that should be considered a warning
HTTP_CODES_WARNING = (404, )

# Text to display when no URI is logged.
URI_ERROR = 'ERROR'
# Text to display when no user agent is logged.
USER_AGENT_UNKNOWN = 'UNKNOWN'

# Log format representing date/time for log entries
LOG_TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
