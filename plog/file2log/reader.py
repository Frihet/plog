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

import time, cStringIO
import plog

class Reader(object):
    """
    Reader class handling input from all registered files, waits for
    input, parses and sends parsed logs to the logger.
    """

    def __init__(self, config, files, logger):
        """
        Initialize the reader, configuration, files and logger should
        have been initialized already.
        """
        # Configuration object
        self.config = config
        # List of file sources
        self.files = files
        # Log output
        self.logger = logger

    def main(self):
        """
        Main routine for the reader, runs a select loop waiting for
        input/errors on the selected files.
        """
        buf = cStringIO.StringIO()
        poller = self._initialize_read(self.files)

        while True:
            # Iterate over files looking for changes, not using poll
            # here as files can change name and thus following path
            # names will not work using the stat approach.
            for f_obj in self.files:
                if f_obj.is_changed():
                    f_obj.reopen()
                if not f_obj.has_data():
                    continue

                # Clears out buffer and reads all the new data in.
                self._read_data(f_obj, buf)

                # Parse, format and send to logger
                self.logger.log(
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
