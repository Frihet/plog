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
Tail file implementation used to watch files by path.
"""

import fcntl, os

class File(object):
    """
    File object containing information about a single file source.
    """

    def __init__(self, name, path, parser):
        """
        Initialize file source.
        """
        # Name of the file, used in formatting.
        self.name = name
        # Path to file, used to keep track of re-names.
        self.path = path
        # Parser for file.
        self.parser = parser

        # File object, None is not opened.
        self.f_obj = None
        # File descriptor of file, -1 is not opened.
        self.fd_num = -1
        # Position in file since last read.
        self.pos = 0
        # Inode file is associated with.
        self.inode = 0
        # Last reported file size.
        self.size = -1

        # Fill in inode/size information
        self.is_changed()
        
        # Finally, open up the file
        self.open(True)

    def close(self):
        """
        Close file.
        """
        if self.f_obj is not None:
            self.f_obj.close()
            self.f_obj = None
        self.fd_num = -1
        self.pos = 0
        self.inode = 0
        self.size = -1

    def open(self, seek_end=False):
        """
        Open file, set it to be non-blocking and seek to the end of
        it to avoid reading old data.
        """
        try:
            self.f_obj = open(self.path, 'r')
        except IOError:
            return False

        # Open file and seek to end
        self.fd_num = self.f_obj.fileno()
        if seek_end:
            self.f_obj.seek(0, 2)
        self.pos = self.f_obj.tell()

        # Set non-blocking mode
        flags = fcntl.fcntl(self.fd_num, fcntl.F_GETFL)
        fcntl.fcntl(self.fd_num, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def reopen(self):
        """
        Re-open file.
        """
        self.close()
        self.open()

    def is_changed(self):
        """
        Check if file was changed since last read.
        """
        is_changed = False

        # Stat file, check if size is < than last time or if st_ino
        # has changed.
        try:
            stat_res = os.stat(self.path)

            # Check if inode has changed, file has been replaced.
            if stat_res.st_ino != self.inode:
                is_changed = True
                self.inode = stat_res.st_ino

            # Check if size is < than previously recorded, rewind but
            # do not set as changed
            if stat_res.st_size < self.size:
                self.size = stat_res.st_size
                if self.f_obj is not None:
                    self.f_obj.seek(0)

        except IOError:
            # FIXME: File does not exist no access, how to handle?
            pass
        except OSError:
            # FIXME: File does not exist no access, how to handle?
            pass

        return is_changed

    def has_data(self):
        """
        Check if file has data to be read.
        """
        return self.f_obj is not None

    def read(self, num):
        """
        Read at max num bytes from file.
        """
        return self.f_obj.read(num)
