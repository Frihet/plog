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

import ConfigParser
import plog

class PlogConfigParser(ConfigParser.SafeConfigParser):
    """
    Enhanced config parser with simple utilties.
    """

    def get_options(self, section):
        """
        Build dictionary from values in section.
        """
        return dict([(option, self.get(section, option))
                     for option in self.options(section)])

    def get_options_with_prefix(self, section, prefix):
        """
        Return dictionary with option: value from configuration with
        options starting with prefix having the prefixed stripped.
        """
        options = {}

        for option in filter(lambda o: o.startswith(prefix),
                             self.options(section)):
            options[option[len(prefix):]] = self.get(section, option)

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

    def get(self, section, value, default=None):
        """
        Get configuration value, return default value if value or
        section does not exist.
        """
        return self.cfg.get(section, value, default)

    def get_db_config(self):
        """
        Get database configuration as a dictionary.
        """
        db_config = self.cfg.get_options(plog.CFG_SECT_DATABASE)
        if 'port' in db_config:
            # FIXME: How to check for port in a sane fashion
            db_config['port'] = int(db_config['port'])

        return db_config

    def get_log_files(self):
        """
        Return all files specified in the configuration file.
        """
        import plog.file_parsers, plog.formatters, plog.file2log.file

        files = []

        for section in filter(lambda s: s.startswith('file2log-'),
                              self.cfg.sections()):
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

            # Setup formatter
            formatter_name = self.cfg.get(
                section, plog.CFG_OPT_FORMATTER, plog.DEFAULT_FORMATTER)
            formatter_options = self.cfg.get_options_with_prefix(
                section, plog.CFG_OPT_FORMATTER + '-')
            formatter = plog.formatters.get_formatter(
                formatter_name, formatter_options)

            # Construct and append
            files.append(plog.file2log.file.File(name, path, parser, formatter))
            
        return files