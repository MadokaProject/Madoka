mysql: ALTER TABLE config MODIFY value MEDIUMTEXT NOT NULL;
mysql: ALTER TABLE msg MODIFY content MEDIUMTEXT NOT NULL;
sqlite: ALTER TABLE config RENAME TO _config_old;
sqlite: CREATE TABLE config (
  name VARCHAR(255) NOT NULL,
  uid char(10) NOT NULL,
  value TEXT NOT NULL,
  PRIMARY KEY (name, uid)
);
sqlite: INSERT INTO config SELECT name, uid, value FROM _config_old;
sqlite: DROP TABLE _config_old;
sqlite: ALTER TABLE msg RENAME TO _msg_old;
sqlite: CREATE TABLE msg (
  id INTEGER AUTO_INCREMENT PRIMARY KEY,
  uid CHAR(10) NOT NULL,
  qid CHAR(12) NOT NULL,
  datetime DATETIME NOT NULL,
  content TEXT NOT NULL
);
sqlite: INSERT INTO msg SELECT id, uid, qid, datetime, content FROM _msg_old;
sqlite: DROP TABLE _msg_old;
