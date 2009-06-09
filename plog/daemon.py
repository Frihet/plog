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
Daemon implementation adding background execute support for
Applications.
"""

import os, logging
import plog, plog.application, plog.util

class Daemon(plog.application.Application):
    """
    An application supporting running in the background.
    """

    def _application_main(self):
        """
        Daemonize if requested in the parameters and then run
        _daemon_main.
        """
        if self._do_daemonize():
            self._daemonize()
        self._daemon_main()

    def _daemon_main(self):
        """
        Daemon main routine, implemented by subclasses.
        """
        raise NotImplementedError()

    def _daemonize(self):
        """
        Daemonize application, writing file with pid if requested.
        """
        try:
            pid = os.fork()
        except OSError, exc:
            raise Exception('failed to fork: %s' % (exc.strerror, ))

        if pid == 0:
            # Initial child, set session id.
            os.setsid()

            try:
                pid = os.fork()
            except OSError, exc:
                raise Exception('failed to fork: %s' % (exc.strerror, ))
            
            if pid == 0:
                # Second child, change work directory to avoid issues
                # locking file mounts.
                os.chdir('/')
            else:
                # First child, exit
                os._exit(0)

        else:
            # Original process, exit with _exit to avoid exit handlers
            # to be run and file descriptors to be flushed.
            os._exit(0)

        # Write pid file if requested
        pid_path = self._config.get(self._name, plog.CFG_OPT_PID_PATH, None)
        if pid_path is not None:
            pid_file = os.path.join(pid_path, '%s.pid' % (self._name, ))
            if not plog.util.write_file(pid_file, str(os.getpid())):
                logging.error('failed to write pid to %s' % (pid_file, ))
            
    def _do_daemonize(self):
        """
        Return true if the daemon should fork off to the background.
        """      
        return self._config.get_bool(self._name, plog.CFG_OPT_DAEMONIZE, '1')
