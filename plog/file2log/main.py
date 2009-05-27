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

import sys, time, cStringIO
import plog, plog.config, plog.daemon, plog.file2log.logger

class File2LogDaemon(plog.daemon.Daemon):
    """
    Reader class handling input from all registered files, waits for
    input, parses and sends parsed logs to the logger.
    """

    def _daemon_main(self):
        """
        Main routine for the reader, runs a select loop waiting for
        input/errors on the selected files.
        """
        # FIXME: Files

        self._logger = plog.file2log.logger.Logger(self._config)
        self._files = self._config.get_log_files()

        buf = cStringIO.StringIO()
        poller = self._initialize_read(self._files)

        while True:
            # Iterate over files looking for changes, not using poll
            # here as files can change name and thus following path
            # names will not work using the stat approach.
            for f_obj in self._files:
                if f_obj.is_changed():
                    f_obj.reopen()
                if not f_obj.has_data():
                    continue

                # Clears out buffer and reads all the new data in.
                self._read_data(f_obj, buf)

                # Parse, format and send to logger
                self._logger.log(
                    map(lambda e: f_obj.formatter.format(f_obj, e),
                        f_obj.parser.feed(buf.getvalue())))

            # Wait and do another round
            time.sleep(plog.READ_INTERVAL)

    def _initialize_read(self, files):
        """
        Initialize reading of files, resetting position, mtimes etc.
        """
        # FIXME: Implement Reader._initialize_read

    def _read_data(self, f_obj, buf):
        """
        Read to end of file appending data read to buf.
        """
        # Reset buffer before starting to read.
        buf.reset()
        buf.truncate()

        # Read data up until READ_MAX and return 
        buf.write(f_obj.read(plog.READ_MAX))

def main():
    """
    Main routine, entry point for application.
    """
    application = File2LogDaemon()
    application.main()

if __name__ == '__main__':
    main()
