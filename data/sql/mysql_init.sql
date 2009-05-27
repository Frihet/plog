-- Table holding meta data information about the database
CREATE TABLE plog_info (
       name VARCHAR(64) NOT NULL,
       value VARCHAR(255) NOT NULL,
       PRIMARY KEY(name)
);

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

-- Table holding single log entries
CREATE TABLE logs (
       id INTEGER NOT NULL AUTO_INCREMENT,
       facility INTEGER NOT NULL DEFAULT 0,
       priority INTEGER NOT NULL DEFAULT 0,
       text TEXT,
       extra_text TEXT,
       host_id INTEGER REFERENCES hosts(id),
       FULLTEXT (text,extra_text), -- Index log data for searching
       PRIMARY KEY(id)
);

-- Special log type tables

-- Request logs such as Apache
CREATE TABLE logs_extra_request (
       log_id INTEGER NOT NULL REFERENCES logs(id),
       PRIMARY KEY(log_id)
);

-- Application server logs such as Tomcat and Glassfish
CREATE TABLE logs_extra_appserver (
       log_id INTEGER NOT NULL REFERENCES logs(id),
       as_name VARCHAR(64) NOT NULL,
       as_level VARCHAR(16) NOT NULL, -- FIXME: Set to integer value
       PRIMARY KEY(log_id)
);