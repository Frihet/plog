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
Plog configuration parsing.
"""

import logging, ConfigParser
import plog

class PlogConfigParser(ConfigParser.SafeConfigParser):
    """
    Enhanced config parser with simple utilties.
    """

    def get_options(self, section):
        """
        Build dictionary from values in section.
        """
        try:
            options = dict([(option, self.get(section, option))
                            for option in self.options(section)])
        except ConfigParser.NoSectionError:
            options = {}
        return options

    def get_options_with_prefix(self, section, pre):
        """
        Return dictionary with option: value from configuration with
        options starting with prefix having the prefixed stripped.
        """
        options = {}

        for option in [o for o in self.options(section) if o.startswith(pre)]:
            options[option[len(pre):]] = self.get(section, option)

        return options

class Config(object):
    """
    Configuration data abstractions, reads the configuration files.
    """

    def __init__(self, path=None):
        """
        Initialize and read the configuration. Gets the path from
        constants if not specified.
        """
        if path is None:
            path = plog.PATH_CONFIG

        # Path to configuration file.
        self.path = path
        # Configuration parser.
        self.cfg = PlogConfigParser()
        self.cfg.read(self.path)

    def get(self, section, key, default=None):
        """
        Get configuration value, return default value if value or
        section does not exist.
        """
        try:
            value = self.cfg.get(section, key)
        except ConfigParser.NoSectionError:
            value = default
        except ConfigParser.NoOptionError:
            value = default
        return value

    def get_bool(self, section, key, default):
        """
        Get boolean value from configuration file.
        """
        value = self.get(section, key, default).lower()
        try:
            value = self._to_bool(value)
        except ValueError:
            logging.warning(
                'invalid boolean in configuration %s.%s, setting default %s'
                % (section, key, default))
            value = self._to_bool(value)

    def _to_bool(self, value):
        """
        Get boolean from string, raise Value
        """
        if value in ('1', 'yes', 'true'):
            value = True
        elif value in ('0', 'no', 'false'):
            value = False
        else:
            raise ValueError('invalid boolean value %s' % (value, ))

    def get_int(self, section, key, default):
        """
        Get integer value from configuration file.
        """
        value = self.get(section, key, default)
        try:
            value = int(value)
        except ValueError:
            logging.warning(
                'invalid integer in configuration %s.%s, setting default %s'
                % (section, key, default))
            value = int(default)
        return value
        

    def get_db_config(self):
        """
        Get database configuration as a dictionary.
        """
        db_config = self.cfg.get_options(plog.CFG_SECT_DATABASE)
        if 'port' in db_config:
            try:
                db_config['port'] = int(db_config['port'])
            except ValueError:
                # FIXME: Send out "feedback" exception
                pass

        return db_config

    def get_log_files(self):
        """
        Return all files specified in the configuration file.
        """
        import plog.file_parsers, plog.file2log.file

        files = []

        sections = [s for s in self.cfg.sections() if s.startswith('file2log-')]
        for section in sections:
            # Get file options
            name = section[len('file-'):]
            path = self.cfg.get(section, plog.CFG_OPT_PATH)

            # Setup parser
            parser_name = self.cfg.get(
                section, plog.CFG_OPT_PARSER, plog.DEFAULT_PARSER)
            parser_options = self.cfg.get_options_with_prefix(
                section, plog.CFG_OPT_PARSER + '-')
            parser = plog.file_parsers.get_parser(
                parser_name, parser_options)

            # Construct and append
            files.append(plog.file2log.file.File(name, path, parser))
            
        return files
