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

        # Construct URLs used for retrieving logs
        url_check = req.container.construct_url(
            req, 'index', 'json_last_modified', search_params)
        url_load = req.container.construct_url(
            req, 'index', 'ajax_logs', search_params)

        return phew.result.Result(
            'index', {'title': 'plog',
                      'form_search': form_search,
                      'url_check': url_check,
                      'url_load': url_load}
            )

    def action_json_last_modified(self, req):
        """
        Perform search with with supplied criteria return a simple
        JSON object with last_modified attribute set to unix
        timestamp of the last log message.
        """
        form_search = plog.frontend.entities.SearchFilter(req)
        if form_search.validate_all():
            last_modified = self.get_last_modified(req, form_search)
        else:
            last_modified = 0

        return phew.result.Result(
            'json_last_modified', {'last_modified': last_modified})

    def action_ajax_logs(self, req):
        """
        Return HTML formatted logs.
        """
        form_search = plog.frontend.entities.SearchFilter(req)
        if form_search.validate_all():
            logs = self.get_logs(req, form_search)
        else:
            logs = []            

        return phew.result.Result('ajax_logs', {'logs': logs})

    def get_last_modified(self, req, form_search):
        """
        Return last modified for search form criteria.
        """
        # FIXME: Implement error handling
        sql_where, sql_params = form_search.get_sql_where()
        sql_query = """SELECT UNIX_TIMESTAMP(logs.log_time) AS last_modified
FROM logs WHERE %s
ORDER BY logs.log_time DESC LIMIT 1""" % (sql_where, )

        row = req.container.db.fetch_one(sql_query, sql_params)

        return row and row['last_modified'] or 0

    def get_logs(self, req, form_search):
        """
        Return logs for search form criteria.
        """
        # FIXME: Error handling, number of entries to load.
        sql_where, sql_params = form_search.get_sql_where()
        sql_query = """SELECT logs.*, hosts.name AS host_name
FROM logs, hosts WHERE logs.host_id = hosts.id AND %s
ORDER BY logs.log_time DESC LIMIT 25""" % (sql_where, )

        return req.container.db.fetch_all(sql_query, sql_params)
