mysql: ALTER TABLE user DROP english_answer;
mysql: ALTER TABLE user DROP last_login;
mysql: ALTER TABLE user DROP points;
mysql: ALTER TABLE user DROP signin_points;
mysql: ALTER TABLE user MODIFY uid char(12) not null;
mysql: ALTER TABLE `group` ADD PRIMARY KEY (uid);

sqlite: ALTER TABLE user RENAME TO _user_old;
sqlite: CREATE TABLE user as SELECT id, uid, active, level, permission FROM _user_old;
sqlite: DROP TABLE _user_old;
sqlite: ALTER TABLE `group` RENAME TO _group_old;
sqlite: CREATE TABLE `group` (
    uid CHAR(12) NOT NULL PRIMARY KEY,
    permission VARCHAR(512) NOT NULL,
    active INT NOT NULL
);
sqlite: INSERT INTO `group` SELECT uid, permission, active FROM _group_old;
sqlite: DROP TABLE _group_old;