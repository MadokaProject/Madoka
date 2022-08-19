ALTER TABLE user DROP english_answer;
ALTER TABLE user DROP last_login;
ALTER TABLE user DROP points;
ALTER TABLE user DROP signin_points;
ALTER TABLE user MODIFY uid char(12) not null;
ALTER TABLE `group` ADD PRIMARY KEY (uid);