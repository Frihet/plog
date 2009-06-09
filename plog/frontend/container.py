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
Plog containers, adding database connection (plog.orm) and plog
configuration to standard phew containers.
"""

import phew.container
import plog.config, plog.orm

class ContainerCGI(phew.container.ContainerCGI):
    """
    Plog CGI container adding plog database connection handling to
    phew containers.
    """

    def __init__(self, config, app):
        """
        Initialize container setting up database resources.
        """
        phew.container.ContainerCGI.__init__(self, config, app)        

        # Plog configuration
        self._plog_config = plog.config.Config()
        # Database connection, wrapped by property.
        self._db = None

    def _get_db(self):
        """
        Get database, init connection if required.
        """
        if self._db is None:
            self._db = plog.orm.get_connection(
                self._plog_config.get_db_config())
        return self._db
    # Database connection property.
    db = property(_get_db)


class ContainerModPython(phew.container.ContainerModPython):
    """
    Plog ModPython container adding plog database connection handling to
    phew containers.
    """

    def __init__(self, config, app):
        """
        Initialize container setup database resources.
        """
        phew.container.ContainerModPython.__init__(self, config, app)

        # Plog configuration
        self._plog_config = plog.config.Config()
        # Dictionary with thread to database mapping.
        self._db_lookup = { }

    def _get_db(self):
        """
        Get database, init connection for each thread.
        """
        import thread
        thread_id = thread.get_ident()

        if thread_id not in self._db_lookup:
            self._db_lookup[thread_id] = plog.orm.get_connection(
                self._plog_config.get_db_config())

        return self._db_lookup[thread_id]
    # DB connection, returns new connection for each thread.
    db = property(_get_db)
