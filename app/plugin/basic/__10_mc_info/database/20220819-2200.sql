mysql: ALTER TABLE mc_server CHANGE ip host VARCHAR(255) NOT NULL;
mysql: ALTER TABLE mc_server MODIFY report VARCHAR(255) NULL;
mysql: ALTER TABLE mc_server ADD PRIMARY KEY (host, port);

sqlite: ALTER TABLE mc_server RENAME TO _mc_server_old;
sqlite: CREATE TABLE mc_server (
    host VARCHAR(255) NOT NULL,
    port char(5) NOT NULL,
    report VARCHAR(255) NULL,
    listen INTEGER DEFAULT 0,
    `default` INTEGER DEFAULT 0,
    delay INTEGER DEFAULT 60,
    PRIMARY KEY (host, port)
);
sqlite: INSERT INTO mc_server SELECT ip, port, report, listen, `default`, delay FROM _mc_server_old;
sqlite: DROP TABLE _mc_server_old;
