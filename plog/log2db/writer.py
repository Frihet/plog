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
log2db writer implementation.
"""

import threading, logging
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

    def stop(self):
        """
        Signal the writer to shut down.
        """
        self._event_queue_cond.acquire()
        self._event_queue = [None]
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
                import traceback
                logging.error('failed to write event %s to database'
                              % (event, ))
                logging.error('write traceback:\n%s'
                             % (traceback.format_exc(), ))
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

        # Host cache
        self._cache_host = plog.util.DictCache(plog.CACHE_MAX_SIZE)
        # Source cache
        self._cache_source = plog.util.DictCache(plog.CACHE_MAX_SIZE)

    def _initialize_run(self):
        """
        Initialize database connection before accepting events.
        """
        try:
            self._conn = plog.orm.get_connection(self._config.get_db_config())
            # As this is a long-running daemon, do not give up connecting to
            # the database.
            self._conn.retry_attempts = -1
            self._conn.retry_interval = plog.LOG2DB_RETRY_INTERVAL
        except plog.DBException:
            raise plog.InitializationError()

    def _shutdown_run(self):
        """
        Close database connection after processing.
        """
        self._conn = None

    def _get_host(self, ip_addr):
        """
        Get host from cache or save to database if not found, should
        always return a value.
        """
        host = self._cache_host.get(ip_addr)
        if host is None:
            host = plog.orm.Host(self._conn, ip=ip_addr)
            if host.id is None:
                host.name = ip_addr
                host.save()
            self._cache_host.set(ip_addr, host)
        return host


    def _get_source(self, name):
        """
        Get source from cache or save to database if not found, should
        always return a value.
        """
        source = self._cache_source.get(name)
        if source is None:
            source = plog.orm.Source(self._conn, name=name)
            if source.id is None:
                source.name = name
                source.save()
            self._cache_source.set(name, source)
        return source

    def _write(self, entry):
        """
        Write message to database.
        """
        host = self._get_host(entry.ip_addr)
        source = self._get_source(entry.name)

        # Main log data
        log_data = {
            'log_type_id': entry.get_log_type(),
            'log_time': entry._get_timestamp_str(),
            'facility': entry.facility, 'priority': entry.level,
            'msg': entry.msg, 'msg_extra': entry.msg_extra,
            'host_id': host.id, 'source_id': source.id
            }

        # Add extra data to log entry
        if entry.extra_values:
            extra_fields = entry.get_extra_fields()
            for pos in xrange(len(extra_fields)):
                log_data[extra_fields[pos][0]] = entry.extra_values[pos]

        # Create log entry, write it
        log = plog.orm.Log(self._conn, **log_data)
        log.save()
