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
Plog entities, both web-only entities and mappings to phew orm objects
is done here.
"""

import time
import phew.entity
import plog.orm

class SearchFilter(phew.entity.FormEntity):
    """
    Entity for handling search forms, filtering and searching.
    """

    # Dict with field information for search filter.
    SEARCH_FIELDS = {
        'environment': phew.entity.FieldInfo(
            list, u'0', 'Environment', values=[(u'0', u'ALL')]),
        'host': phew.entity.FieldInfo(
            list, u'0', 'Host', values=[(u'0', u'ALL')]),
        'source': phew.entity.FieldInfo(
            list, u'0', 'Source', values=[(u'0', u'ALL')]),
        # FIXME: Get list from entry module?
        'priority': phew.entity.FieldInfo(
            list, u'-1', 'Log level', values=[
                (u'-1', u''),
                (u'7', u'&gt;= DEBUG'), (u'6', u'&gt;= INFO'),
                (u'5', u'&gt;= NOTICE'), (u'4', u'&gt;= WARNING'),
                (u'3', u'&gt;= ERR'),  (u'2', u'&gt;= CRIT'),
                (u'1', u'&gt;= ALERT'),(u'0', u'= EMERG'),
                ]),
        'refresh': phew.entity.FieldInfo(
            bool, False, 'Follow logs'),
        'search': phew.entity.FieldInfo(unicode, u'', 'Search'),
        'time_start': phew.entity.FieldInfo(
            time.struct_time, time.localtime(time.time() - 3600), 'Start'),
        'time_end': phew.entity.FieldInfo(
            time.struct_time, time.localtime(time.time() + 3600), 'End'),
        'last_id': phew.entity.FieldInfo(int, None, None, False)
        }

    def __init__(self, req):
        """
        Initialize filter, setting default values of search.
        """
        # Set field values before calling parent init making sure
        # attribute access behaves as expected.
        self.environment = None
        self.host = u'0'
        self.priority = u'-1'
        self.refresh = False
        self.search = u''
        self.time_start = None
        self.time_end = None
        self.last_id = 0

        # Try to lookup hosts if not done already (empty list).
        host_values = SearchFilter.SEARCH_FIELDS['host'].list_values
        if  len(host_values) == 1:
            for host in plog.orm.Host.find_all(
                req.container.db, {}, 'name'):
                host_values.append((unicode(host.id), host.name))

        # Try to lookup source if not done already (empty list).
        source_values = SearchFilter.SEARCH_FIELDS['source'].list_values
        if  len(source_values) == 1:
            for source in plog.orm.Source.find_all(
                req.container.db, {}, 'name'):
                source_values.append((unicode(source.id), source.name))

        # Attributes set, call parent
        phew.entity.FormEntity.__init__(self, 'search', req)

    def get_fields(self):
        """
        Return field information in dict with name: FieldInfo
        pairs. FieldInfo can be None.
        """
        return SearchFilter.SEARCH_FIELDS        

    def get_sql_where(self):
        """
        Return (sql, parameters) tuple for filtering in the database
        on specified parameters.
        """
        query_parts = ['logs.log_time >= %s', 'logs.log_time <= %s']
        query_params = [phew.util.value_to_str(self.time_start),
                        phew.util.value_to_str(self.time_end)]

        host_id = int(self.host)
        if host_id > 0:
            query_parts.append('logs.host_id = %s')
            query_params.append(host_id)
        priority_id = int(self.priority)
        if priority_id > -1:
            query_parts.append('logs.priority <= %s')
            query_params.append(priority_id)

        if self.search:
            query_parts.append("""MATCH(logs.msg, logs.msg_extra)
AGAINST (%s IN BOOLEAN MODE)""")
            query_params.append(self.search)

        return (' AND '.join(query_parts), query_params)
