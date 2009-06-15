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
Database connection handling and simple object mappings.
"""

import logging, sys, time
import MySQLdb


# Set to true when database information has been extracted
DB_INITIALIZED = False

class DBObject(object):
    """
    Base class for database mapped objects.
    """

    def __init__(self, conn, **kwargs):
        """
        Initialize DBObject, if only 1 kwarg is given use that trying
        to lookup the object, else set values.

        FIXME: Currently no validation is done on the column names to
               avoid speed-downs, this should be an optional parameter.
        """
        # Database connection handle
        self._conn = conn

        init_object = True

        # Get key to lookup object from database with
        if len(kwargs) == 1:
            lookup_key = kwargs.keys()[0]
        else:
            lookup_key = None

        if lookup_key is not None:
            init_object = not self.find({ lookup_key: kwargs[lookup_key]})

        if init_object:
            self._init_object()
            for column, value in kwargs.iteritems():
                setattr(self, column, value)

    def _init_object(self):
        """
        Initialize object setting column default values.
        """
        for column in self.get_column_names():
            setattr(self, column, None)

    @classmethod
    def _get_conditions(cls, conditions):
        """
        Get SQL conditions from dictionary.
        """
        sql_params = [conditions[name] for name in conditions.keys()]
        sql = ', '.join(['%s=%%s' % (name, ) for name in conditions.keys()])

        return (sql, sql_params)

    def find(self, conditions):
        """
        Find DBObject based on conditions. Conditions is a dict
        holding column -> value conditions.
        """
        # Build find query
        conditions_sql, conditions_params = self._get_conditions(conditions)
        if conditions_sql:
            query = """SELECT * FROM %s WHERE %s""" % (
                self.get_table_name(), conditions_sql)
        else:
            query = """SELECT * FROM %s WHERE %s""" % (self.get_table_name(), )

        # Fetch results and set
        row = self._conn.fetch_one(query, conditions_params)
        if row is not None:
            for column, value in row.iteritems():
                setattr(self, column, value)

        return row is not None

    @classmethod
    def find_all(cls, conn, conditions, order_by=None, limit_offset=None):
        """
        Find all DBObjects matching condition returning a list.
        """
        objects = []

        # Build find query
        conditions_sql, conditions_params = cls._get_conditions(conditions)
        if conditions_sql:
            query = """SELECT * FROM %s WHERE %s""" % (
                cls.get_table_name(), conditions_sql)
        else:
            query = """SELECT * FROM %s""" % (cls.get_table_name(), )

        if order_by is not None:
            query += " ORDER BY %s" % (order_by, )
        if limit_offset is not None:
            query += " LIMIT %d, OFFSET %d" % (limit_offset[0], limit_offset[1])

        # Fetch results and set
        rows = conn.fetch_all(query, conditions_params)
        for row in rows:
            objects.append(cls(conn, **dict(row.iteritems())))

        return objects

    def save(self):
        """
        Insert object into database.
        """
        # FIXME: Implement validation, columns need to exist etc

        query_params = [getattr(self, col, None)
                        for col in self.get_column_names(False)]
        query = """INSERT INTO %s (%s) VALUES (%s)""" % (
            self.get_table_name(),
            ', '.join(self.get_column_names(False)),
            ', '.join(['%s' for col in self.get_column_names(False)]))

        # FIXME: Do not assume there is an auto_increment column
        # Save and set last_id
        self._conn.execute(query, query_params)
        setattr(self, self.get_primary_key(), self._conn.get_insert_id())

    def update(self):
        """
        Update already existing object.
        """
        # Build conditions based on single primary key.
        conditions_sql, conditions_params = self._get_conditions(
            {self.get_primary_key(): getattr(self, self.get_primary_key())})

        # Update all but the primary key
        update_params = [getattr(self, col)
                         for col in self.get_column_names(False)]
        update = ', '.join(['%s=%%s' % (col, )
                            for col in self.get_column_names(False)])

        # Build complete query
        query_params = update_params + conditions_params
        query = """UPDATE %s SET %s WHERE %s""" % (
            self.get_table_name(), update, conditions_sql)

        self._conn.execute(query, query_params)

    def save_or_update(self):
        """
        Save or update object depending on if it already exists.
        """
        if getattr(self, self.get_primary_key(), None) is None:
            self.save()
        else:
            self.update()

    @classmethod
    def get_table_name(cls):
        """
        Get name of the table, implemented by sub-classes.
        """
        raise NotImplementedError()

    @classmethod
    def get_primary_key(cls):
        """
        Get primary key for object.

        FIXME: This currently only returns id, should be introspected.
        """
        return 'id'

    @classmethod
    def get_column_names(cls, include_primary=True):
        """
        Get list of column names.
        """
        if include_primary:
            return cls._COLUMNS.keys()
        else:
            return cls._COLUMNS_NO_PRIMARY

    @classmethod
    def set_column_list(cls, columns):
        """
        Get name of the table, implemented by sub-classes.
        """
        cls._COLUMNS = columns
        cls._COLUMNS_NO_PRIMARY = [col for col in columns.keys()
                                   if col not in cls.get_primary_key()]

class Environment(DBObject):
    """
    Named grouping of a set of hosts.
    """

    @classmethod
    def get_table_name(cls):
        """
        Get name of the table.
        """
        return 'environments'

class Host(DBObject):
    """
    Single log source, associated with an IP address.
    """

    @classmethod
    def get_table_name(cls):
        """
        Get name of the table.
        """
        return 'hosts'

class HostType(DBObject):
    """
    Type of host, used in the frontend.
    """

    @classmethod
    def get_table_name(cls):
        """
        Get name of the table.
        """
        return 'host_types'

class Source(DBObject):
    """
    Type of log source.
    """

    @classmethod
    def get_table_name(cls):
        """
        Get name of the table.
        """     
        return 'log_sources'

class Log(DBObject):
    """
    Single log entry, can be complemented with extra data from other
    log objects such as LogExtraAppserver.
    """

    @classmethod
    def get_table_name(cls):
        """
        Get name of the table.
        """
        return 'logs'

def try_reconnect(fn):
    """
    Reconnect decorator, retries up until retry_attempts on instance or
    been done. If instance retry_interval is > 0, sleep that long between
    attempts.
    """

    # Allowed operational errors, access denied, can't connect, unknown host
    # and gone away.
    ALLOWED_CONNECT_ERRORS = (1045, 2003, 2005, 2006)

    def do_retry(*args):
        """
        Retry part of decorator, separated out to not slow queries that work
        ok.
        """
        # FIXME: How to get instance object in a sane fashion?
        obj = getattr(fn, 'im_self', args[0])

        num = 0
        while obj.retry_attempts == -1 or num < obj.retry_attempts:
            # If connection failed and more retry attempts exist,
            # sleep for a while before retrying.
            if obj.retry_interval > 0:
                time.sleep(obj.retry_interval)

            # Re-execute query
            if obj.is_connected():
                try:
                    return fn(*args)
                except MySQLdb.OperationalError, exc:
                    if exc.args[0] != 2006:
                        raise
                    logging.debug('lost connection to server, attempt %d'
                                  % (num, ))

            # Re-connect if connection is still broken, allow for most 
            try:
                obj.connect()
            except MySQLdb.OperationalError, exc: 
                if exc.args[0] not in ALLOWED_CONNECT_ERRORS:
                    raise 
                logging.debug('failed to reconnect after failure, attempt %d'
                              % (num, ))
            num += 1
        raise # FIXME: Sane exception

    def retry(*args):
        """
        Main decorator, try and if it fails send query over to retry handler.
        """
        try:
            return fn(*args)
        except MySQLdb.OperationalError, exc:
            if exc.args[0] != 2006:
                raise
            do_retry(*args)

    return retry

class DBConnection(object):
    """
    Base class for database connections.
    """

    def __init__(self, conn_info):
        """
        Validate parameters.
        """
        # How many times should connection to the database re-tried,
        # -1 is unlimited.
        self.retry_attempts = -1
        # How many seconds should be waited until retrying an
        # connection, <= 0 disabled waiting.
        self.retry_interval = 0.05
        # Database connection handle
        self._conn = None

        for parameter in self._get_required_parameters():
            if parameter not in conn_info or not conn_info[parameter]:
                raise ValueError(
                    'missing/empty parameter %s. parameters required are %s'
                    % (parameter, ', '.join(self._get_required_parameters())))

    def _get_required_parameters(self):
        """
        Get list of required parameters, implemented by sub classes.
        """
        raise NotImplementedError()

    def connect(self, conn_info=None):
        """
        Connect to database, if already connected close connection and
        re-connect.
        """
        if self._conn is not None:
            self._conn = None
        if conn_info is None:
            conn_info = self._conn_info

        self._connect(conn_info)
        self._conn_info = conn_info

    def _connect(self, conn_info):
        """
        Actual DB connection method, implemented by subclasses.
        """
        raise NotImplementedError()

    def is_connected(self):
        """
        Return True if database is connected, not validated.
        """
        return self._conn is not None

    def get_cursor(self):
        """
        Get cursor for database connection, implemented by sub classes.
        """
        raise NotImplementedError()

    @try_reconnect
    def execute(self, query, query_params):
        """
        Execute query not returning results.
        """
        curs = self.get_cursor()
        if query_params:
            res = curs.execute(query, query_params)
        else:
            res = curs.execute(query)
        curs.close()

    @try_reconnect
    def fetch_one(self, query, query_params):
        """
        Convenience functionality to fetch to grab a cursor, execute a
        query and return a dictionary with the results.
        """
        curs = self.get_cursor()
        if query_params:
            res = curs.execute(query, query_params)
        else:
            res = curs.execute(query)
        row = curs.fetchone()
        curs.close()

        return row

    @try_reconnect
    def fetch_all(self, query, query_params):
        """
        Convenience functionality to fetch all results for a
        query. Grabs cursor, executes and returns a list of rows.
        """
        curs = self.get_cursor()
        if query_params:
            res = curs.execute(query, query_params)
        else:
            res = curs.execute(query)

        rows = []
        row = curs.fetchone()
        while row:
            rows.append(row)
            row = curs.fetchone()
        curs.close()

        return rows

class MySQLDBConnection(DBConnection):
    """
    MySQL database connection.
    """
    
    def __init__(self, conn_info):
        """
        Initialize database connection.
        """
        DBConnection.__init__(self, conn_info)

        self.connect(conn_info)

    def _get_required_parameters(self):
        """
        Return required parameters for a MySQL connection.
        """
        return ('host', 'port', 'username', 'password', 'db_name')

    def _connect(self, conn_info):
        """
        Open connection to MySQL and store handle on self.
        """
        # MySQL datbase connection handle
        self._conn = MySQLdb.connect(
            user=conn_info['username'], passwd=conn_info['password'],
            host=conn_info['host'], port=conn_info['port'],
            db=conn_info['db_name'], use_unicode=True) 

    def get_cursor(self):
        """
        Return cursor for database connection.
        """
        return self._conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

    def get_insert_id(self):
        """
        Return the last inserted id.
        """
        return self._conn.insert_id()

    def get_table_column_list(self, table_name):
        """
        Get column list for object.
        """
        curs = self.get_cursor()
        res = curs.execute("""SELECT * FROM %s LIMIT 1""" % (table_name, ))
        columns = dict((col[0], col[1]) for col in curs.description)
        curs.close()

        return columns

def get_connection(conn_info):
    """
    Get database connection. conn_info is a dictionary with the
    following parameters required:

      * db_type, currently this needs to be set to MySQL.
      * host, host where database resides.
      * port, port to connect on.
      * username, username to connect with.
      * password, password to connect with.
      * db_name, name of the database.

    @param conn_info Dictionary with connection information.
    """
    assert isinstance(conn_info, dict)
    if 'db_type' not in conn_info or not conn_info['db_type']:
        raise ValueError(
            'missing db_type parameter, currently mysql is supported')

    # Get database
    if conn_info['db_type'].lower() == 'mysql':
        conn = MySQLDBConnection(conn_info)
    else:
        raise ValueError(
            'unsupported database type %s, currently mysql is supported'
            % (conn_info['db_type'], ))

    # Initialize database if not already done.
    module = sys.modules[__name__]
    if not module.DB_INITIALIZED:
        _initialize_db(conn)
        module.DB_INITIALIZED = True

    return conn

def _initialize_db(conn):
    """
    Initialize database object mappings, loop through objects in
    module and initialize classes with DBObject in their inheritance.
    """
    module = sys.modules[__name__]

    for name in dir(module):
        # Skip protected/private members
        if name.startswith('_') or name == 'DBObject':
            continue

        member = getattr(module, name)
        if type(member) is type and issubclass(member, DBObject):
            # If it is a db object, get the table and load information
            # about it.
            columns = conn.get_table_column_list(member.get_table_name())
            member.set_column_list(columns)
