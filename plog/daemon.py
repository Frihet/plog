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

import plog, plog.application

class Daemon(plog.application.Application):
    """
    An application supporting running in the background.
    """

    def _application_main(self):
        """
        Daemonize if requested in the parameters and then run
        _daemon_main.
        """
        if False:
            # FIXME: Implement daemoninzation
            pass

        # FIXME: Implement child respawn

        self._daemon_main()

    def _daemon_main(self):
        """
        Daemon main routine, implemented by subclasses.
        """
        raise NotImplementedError()
