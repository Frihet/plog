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
file2log main routine.
"""

import time, cStringIO
import plog, plog.config, plog.daemon, plog.file2log.logger

class File2LogDaemon(plog.daemon.Daemon):
    """
    Reader class handling input from all registered files, waits for
    input, parses and sends parsed logs to the logger.
    """

    def __init__(self):
        """
        Initialize File2LogDaemon
        """
        plog.daemon.Daemon.__init__(self, 'file2log')

        # Log writer, used to send logs via syslog
        self._logger = None
        # List of file information objects
        self._files = None

    def _daemon_main(self):
        """
        Main routine for the reader, runs a select loop waiting for
        input/errors on the selected files.
        """
        self._drop_privileges()

        # Init and read configuration
        self._logger = plog.file2log.logger.Logger(self._config)
        self._files = self._config.get_log_files()

        buf = cStringIO.StringIO()
        poller = self._initialize_read(self._files)

        read_data = False
        while self._do_run():
            # Iterate over files looking for changes, not using poll
            # here as files can change name and thus following path
            # names will not work using the stat approach.
            for f_obj in self._files:
                # Re-open file if it has been truncated or been replaced.
                if f_obj.is_changed():
                    f_obj.reopen()
                if not f_obj.has_data():
                    continue

                # Try to read data, continue if nothing was returned
                data = f_obj.read(plog.READ_MAX)
                if not data:
                    continue

                # Clears out buffer and reads all the new data in.
                read_data = True
                self._add_data(buf, data)

                # Parse, format and send to logger
                self._logger.log(f_obj.name, f_obj.parser.feed(buf.getvalue()))

            # Wait and do another round
            if not read_data:
                time.sleep(plog.READ_INTERVAL)
            read_data = False

    def _initialize_read(self, files):
        """
        Initialize reading of files, resetting position, mtimes etc.
        """
        # FIXME: Implement Reader._initialize_read

    def _add_data(self, buf, data):
        """
        Read to end of file appending data read to buf.
        """
        # Reset buffer before starting to read.
        buf.reset()
        buf.truncate()

        # Read data up until READ_MAX and return 
        buf.write(data)

def main():
    """
    Main routine, entry point for application.
    """
    application = File2LogDaemon()
    application.main()

if __name__ == '__main__':
    main()
