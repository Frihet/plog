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
Main controller for plog performing display and searching in the log
data.
"""

import time, phew.controller
import plog.orm, plog.frontend.entities

class IndexController(phew.controller.Controller):
    def action_index(self, req):
        """
        Main action, display search filter form.
        """
        form_search = plog.frontend.entities.SearchFilter(req)
        if not form_search.validate_all():
            return

        # Construct search parameters from search form.
        search_params = form_search.params_all()
        search_params_ajax = search_params + \
            [(form_search._get_input_name('page'), form_search.page)]

        # Construct URLs used for retrieving logs
        url_json = req.container.construct_url(
            req, 'index', 'json_logs', search_params)
        url_ajax = req.container.construct_url(
            req, 'index', 'ajax_logs', search_params_ajax)

        return phew.result.Result(
            'index', {'title': 'plog',
                      'form_search': form_search,
                      'url_json': url_json,
                      'url_ajax': url_ajax}
            )

    def action_json_logs(self, req):
        """
        Perform search with with supplied criteria return a simple
        JSON object with last_modified attribute set to unix
        timestamp of the last log message.
        """
        logs = []
        form_search = plog.frontend.entities.SearchFilter(req)
        if form_search.validate_all():
            logs = self.get_logs(
                req, form_search, 'logs.log_time DESC, logs.id ASC')
            if logs:
                last_id = logs[-1]['id']
                last_modified = logs[-1]['log_time_unix']

        if not logs:
            last_id = last_modified = 0

        return phew.result.Result(
            'json_logs', {'last_id': last_id,
                          'last_modified': last_modified,
                          'logs': logs})

    def action_ajax_logs(self, req):
        """
        Return HTML formatted logs.
        """
        form_search = plog.frontend.entities.SearchFilter(req)
        if form_search.validate_all():
            logs = self.get_logs(req, form_search)
        else:
            logs = []

        form_search.count = self.get_logs_count(req, form_search)

        return phew.result.Result(
            'ajax_logs', {'form_search': form_search,
                          'logs': logs
                          })

    def get_logs(self, req, form_search,
                 sql_order_by='logs.log_time DESC, logs.id DESC'):
        """
        Return logs for search form criteria.
        """
        sql_where, sql_params = form_search.get_sql_where()
        if form_search.refresh:
            sql_limit_offset = "LIMIT %s"
            sql_params.append(plog.ORM_MAX_LOAD)
        else:
            # Only add limit / offset when in non tailing mode.
            sql_limit_offset = "LIMIT %s OFFSET %s"
            sql_params.extend((form_search.epp,
                               (form_search.page - 1) * form_search.epp))

        # Assemble query
        sql_query = """SELECT logs.*, 
  UNIX_TIMESTAMP(logs.log_time) AS log_time_unix,
  hosts.name AS host_name,
  log_sources.name AS log_source_name
FROM logs, hosts, log_sources
WHERE logs.host_id = hosts.id AND logs.source_id = log_sources.id AND %s
ORDER BY %s %s""" % (sql_where, sql_order_by, sql_limit_offset)

        # FIXME: Error handling, number of entries to load.
        return req.container.db.fetch_all(sql_query, sql_params)

    def get_logs_count(self, req, form_search):
        """
        Return number of matching log entries for criteria.
        """
        # FIXME: Error handling
        sql_where, sql_params = form_search.get_sql_where()
        sql_query = 'SELECT COUNT(*) AS count FROM logs WHERE %s' % (
            sql_where, )
        return req.container.db.fetch_one(sql_query, sql_params)['count']
