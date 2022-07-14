create table if not exists user
(
    id             int auto_increment comment 'ID' primary key,
    uid            char(12)                 null comment 'QQ',
    permission     varchar(512) default '*' not null comment '许可',
    active         int                      not null comment '状态',
    level          int          default 1   not null comment '权限',
    points         int          default 0   null comment '货币',
    signin_points  int          default 0   null comment '签到货币',
    english_answer int          default 0   null comment '英语答题榜',
    last_login     date comment '最后登陆'
);

create table if not exists `group`
(
    uid        char(12)     null comment '群号',
    permission varchar(512) not null comment '许可',
    active     int          not null comment '状态'
);
