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
Plog utility and convenience functionality.
"""

def write_file(path, data, append=False):
    """
    Write data into file at path.
    """
    try:
        if append:
            f_obj = open(path, 'a')
        else:
            f_obj = open(path, 'a')

        f_obj.write(data)
        f_obj.close()
    except IOError:
        return False
    except OSError:
        return False

    return True

def value_to_str(value):
    """
    Convert value to string.
    """
    if isinstance(value, unicode):
        value = value.encode('utf-8')
    elif isinstance(value, int):
        value = '%d' % (value, )
    elif isinstance(value, float):
        value = '%0.2f' % (value, )
    elif not isinstance(value, str):
        value = str(value)
    return value
