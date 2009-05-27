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

import sys
import plog, plog.config

class Application(object):
    """
    Base class for command line applications, handles parsing of
    arguments, printing help messages and initializing common
    functionality.
    """

    def __init__(self):
        """
        Initialize application.
        """
        # Configuration
        self._config = None

    def print_usage(self):
        """
        Print usage information and exit.
        """
        print >>sys.stderr, "usage: %s%" % (
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

        # FIXME: Initialize logging, signal handler

        # FIXME: Get configuration part from options when option
        # parsing is in place
        self._initialize_config(None)

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

    def _drop_privileges(self, user, group):
        """
        Set user/group privileges
        """
        import os, grp, pwd

        # FIXME: Handle permission exceptions

        user_info = pwd.getpwnam(user)
        group_info = grp.getgrnam(group)

        os.seteuid(user_info.pw_uid)
        os.setegid(group_info.gr_gid)

    def _do_run(self):
        """
        Check if application should continue to run.
        """
        return True