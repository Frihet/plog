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

import threading
import plog, plog.orm

class Writer(threading.Thread):
    """
    Base class for log writers, handles reading of queue events and
    transformation from/to log formats.
    """

    def __init__(self, config):
        """
        Initialize writer, create event queue and run _writer_init.
        """
        threading.Thread.__init__(self)

        # Configuration
        self._config = config
        # List holding queue events
        self._event_queue = []
        # Condition protecting the event queue
        self._event_queue_cond = threading.Condition()

    def _write(self, entry):
        """
        Write entry to writer store, implemented by subclasses.
        """
        raise NotImplementedError()

    def add(self, entry):
        """
        Add classified and parsed log entry.
        """
        self._event_queue_cond.acquire()
        self._event_queue.append(entry)
        self._event_queue_cond.notify()
        self._event_queue_cond.release()

    def run(self):
        """
        Writer main routine, waits for events and _writes them. Exits
        if a None event is found.
        """
        try:
            self._initialize_run()
        except plog.InitializationError:
            return

        event = self._get_event()
        while event is not None:
            # Write event, various kinds of "IO" errors can occur.
            try:
                self._write(event)
            except:
                # FIXME: Valid exceptions and logging
                print " ----- WRITE ERROR -----"
                import traceback
                traceback.print_exc()

            # Get next event
            event = self._get_event()

        self._shutdown_run()

    def _initialize_run(self):
        """
        Called from the main routine before starting. To be
        overridden by subclasses.
        """

    def _shutdown_run(self):
        """
        Called from the main routine after processing is done. To be
        overridden by subclasses.
        """

    def _get_event(self):
        """
        Get event from queue.
        """
        self._event_queue_cond.acquire()
        while len(self._event_queue) == 0:
            self._event_queue_cond.wait()
        event = self._event_queue.pop(0)
        self._event_queue_cond.release()

        return event

class DBWriter(Writer):
    """
    Base class for database writers.
    """

class MySQLDBWriter(DBWriter):
    """
    MySQL DB Writer, stores parsed messages into a MySQL database.
    """

    def __init__(self, config):
        """
        Initialize writer, sets database connection handle.
        """
        DBWriter.__init__(self, config)

        # Database connection handle.
        self._conn = None

    def _initialize_run(self):
        """
        Initialize database connection before accepting events.
        """
        try:
            self._conn = plog.orm.get_connection(self._config.get_db_config())
        except plog.DBException:
            raise plog.InitializationError()

    def _shutdown_run(self):
        """
        Close database connection after processing.
        """
        self._conn.close()
        self._conn = None

    def _write(self, entry):
        """
        Write message to database.
        """
        # FIXME: Add host cache
        host = plog.orm.Host(self._conn, ip=entry.ip)
        if host.id is None:
            host.name = entry.ip
            host.save()

        # Create log entry, write it
        log = plog.orm.Log(
            self._conn,
            facility=entry.facility, priority=entry.priority,
            text=entry.text, extra_text=entry.extra_text, host_id = host.id)
        log.save()

        # Write extra log data if requested
        if entry.extra_class is not None:
            log_extra = entry.extra_class(
                self._conn, log_id=log.id, **entry.extra_params)
            log_extra.save()