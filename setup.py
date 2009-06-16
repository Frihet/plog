#!/usr/bin/env python
# -*- encoding: utf-8 -*-
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

import plog

from distutils.core import setup

setup(name='plog', version=plog.VERSION,
      description='python log utlities',
      author='Claes Nästén', author_email='claes.nasten@freecode.no',
      url='https://projects.freecode.no/projects/show/plog',
      packages=['plog', 'plog.file2log', 'plog.file_parsers',
                'plog.frontend', 'plog.frontend.controllers', 'plog.log2db'],
      package_dir={'plog.frontend': 'plog/frontend'},
      package_data={'plog.frontend': ['templates/*.mako',
                                      'static/css/*.css',
                                      'static/css/images/*.png',
                                      'static/js/*.js',
                                      'static/img/*.png']},
      scripts=['scripts/file2log', 'scripts/log2db'],
      data_files=[('sql', ['data/sql/mysql_init.sql']),
                  ('/etc', ['data/plog.cfg']),
                  ('/etc/init.d', ['data/init/file2log', 'data/init/log2db'])],
      )
