-- Table holding meta data information about the database
CREATE TABLE plog_info (
       name VARCHAR(64) NOT NULL,
       value VARCHAR(255) NOT NULL,
       PRIMARY KEY(name)
);

-- Set schema version
INSERT INTO plog_info (name, value) VALUES ('schema_version', '0.1.0');

-- Table holding environment information
CREATE TABLE environments (
       id INTEGER NOT NULL AUTO_INCREMENT,
       name VARCHAR(64) NOT NULL,
       PRIMARY KEY(id)
);

-- Table holding different types of hosts, used in the frontend
CREATE TABLE host_types (
       id INTEGER NOT NULL AUTO_INCREMENT,
       name VARCHAR(64) NOT NULL,
       PRIMARY KEY(id)
);

-- Table holding log source information
CREATE TABLE hosts (
       id INTEGER NOT NULL AUTO_INCREMENT,
       ip VARCHAR(15) NOT NULL, -- IP address of the host
       name VARCHAR(255) NOT NULL, -- User visible name
       environment_id INTEGER REFERENCES environments(id),
       host_type_id INTEGER REFERENCES host_types(id),
       PRIMARY KEY(id)
);

-- Table holding log type matching, id, name, 
CREATE TABLE log_types (
       id INTEGER NOT NULL,
       name VARCHAR(64) NOT NULL,
       table_name VARCHAR(64),
       PRIMARY KEY(id)
);

-- Insert log types
INSERT INTO log_types (id, name, table_name) VALUES (0, 'plain', NULL);
INSERT INTO log_types (id, name, table_name) VALUES (1, 'request', 'logs_extra_request');
INSERT INTO log_types (id, name, table_name) VALUES (2, 'appserver', 'logs_extra_appserver');

-- Table holding single log entries
CREATE TABLE logs (
       id INTEGER NOT NULL AUTO_INCREMENT,
       log_time TIMESTAMP NOT NULL DEFAULT NOW(),
       facility INTEGER NOT NULL DEFAULT 0,
       priority INTEGER NOT NULL DEFAULT 0,
       text TEXT,
       extra_text TEXT,
       log_type INTEGER REFERENCES log_types(id),
       host_id INTEGER REFERENCES hosts(id),
       re_ip VARCHAR(15) NOT NULL, -- Columns used by request entries
       re_method VARCHAR(16) NOT NULL,
       re_user_agent VARCHAR(255),
       re_size INTEGER NOT NULL DEFAULT 0,
       re_status INTEGER NOT NULL,
       re_ms_time INTEGER NOT NULL DEFAULT 0,
       re_uri VARCHAR(255) NOT NULL,
       as_name VARCHAR(64) NOT NULL, -- Columns used by appserver entries
       as_level VARCHAR(16) NOT NULL, -- FIXME: Set to integer value
       FULLTEXT (text,extra_text), -- Index log data for searching
       PRIMARY KEY(id)
);
