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
Application implementation, handles configuration parsing and
executing of applications.
"""

import logging, os, signal, sys
import plog, plog.config

class Application(object):
    """
    Base class for command line applications, handles parsing of
    arguments, printing help messages and initializing common
    functionality.
    """

    def __init__(self, name):
        """
        Initialize application.
        """
        # Application name
        self._name = name
        # Configuration
        self._config = None
        # Boolean flag to set application should be shut down
        self._flag_run = True
        # Boolean flag to set application should reload it's configuration
        self._flag_reload = False

    def print_usage(self):
        """
        Print usage information and exit.
        """
        print >> sys.stderr, "usage: %s%" % (
            sys.argv[0], self._format_parameters())
        sys.exit(plog.EXIT_USAGE)

    def _format_parameters(self):
        """
        Get application parameters and format then for use in the
        usage information.
        """
        return '' # FIXME: Implement _format_parameters

    def _parse_parameters(self):
        """
        Parse input parameters.
        """
        pass

    def _validate_parameters(self):
        """
        Validate input parameters, implemented by subclasses.
        """
        return True

    def main(self):
        """
        Main routine, initialize and run _application_main
        """
        self._parse_parameters()
        if not self._validate_parameters():
            self.print_usage()

        # FIXME: Get configuration part from options when option
        # parsing is in place
        self._initialize_config(None)
        self._initialize_logging()
        self._initialize_signal_handlers()

        # Initialization is done, start application
        self._application_main()

    def _application_main(self):
        """
        Application main routine, implemented by subclasses.
        """
        raise NotImplementedError()

    def _initialize_config(self, path):
        """
        Read configuration file.
        """
        self._config = plog.config.Config(path)

    def _initialize_logging(self):
        """
        Initialize logging.
        """
        level = self._config.get(plog.CFG_SECT_LOGGING, plog.CFG_OPT_LOG_LEVEL,
                                 plog.CFG_OPT_LOG_LEVEL_DEFAULT)
        level = self._config.get(self._name, plog.CFG_OPT_LOG_LEVEL, level)
        path = self._config.get(plog.CFG_SECT_LOGGING, plog.CFG_OPT_LOG_PATH,
                                 plog.CFG_OPT_LOG_PATH_DEFAULT)

        # Convert log level to logging level
        level = logging._levelNames.get(level.upper(), logging.WARNING)

        # Make sure log path exists and setup log file
        if not os.path.exists(path):
            os.makedirs(path)
        log_path = os.path.join(path, '%s.log' % (self._name, ))

        logging.basicConfig(filename=log_path, level=level)

    def _initialize_signal_handlers(self):
        """
        Initialize application signal handlers.
        """
        signal.signal(signal.SIGINT, self._signal_handle_int)
        signal.signal(signal.SIGHUP, self._signal_handle_hup)

    def _drop_privileges(self, user=None, group=None):
        """
        Set user/group privileges
        """
        import grp, pwd

        # FIXME: Handle permission exceptions

        # Set user privileges
        if user is None:
            user = self._config.get(
                plog.CFG_SECT_GLOBAL, plog.CFG_OPT_USER, None)
            user = self._config.get(self._name, plog.CFG_OPT_USER, user)
        if user is not None:
            user_info = pwd.getpwnam(user)
            os.seteuid(user_info.pw_uid)

        # Set group privileges
        if group is None:
            group = self._config.get(
                plog.CFG_SECT_GLOBAL, plog.CFG_OPT_GROUP, None)
            group = self._config.get(self._name, plog.CFG_OPT_GROUP, group)
        if group is not None:
            group_info = grp.getgrnam(group)
            os.setegid(group_info.gr_gid)

    def stop(self):
        """
        Request the application to shut down.
        """
        self._flag_run = False

    def _do_run(self):
        """
        Check if application should continue to run.
        """
        return self._flag_run

    def reload(self):
        """
        Request the application to reload it's configuration
        """
        self._flag_reload = True

    def _do_reload(self):
        """
        Check if application should re-load it's configuration files.
        """
        return self._flag_reload

    def _signal_handle_hup(self, signum, frame):
        """
        Handle SIGHUP, set reload flag to true.
        """
        assert signum == signal.SIGHUP
        self._flag_reload = True

    def _signal_handle_int(self, signum, frame):
        """
        Handle SIGINT, set run flag to false.
        """
        assert signum == signal.SIGINT
        self._flag_run = False
