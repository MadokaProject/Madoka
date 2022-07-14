create table if not exists msg
(
    id       int auto_increment comment '序号' primary key,
    uid      char(10)     null comment '群号',
    qid      char(12)     null comment 'QQ',
    datetime datetime     not null comment '时间',
    content  varchar(800) not null comment '内容'
);

create table if not exists mc_server
(
    ip        char(15)     not null comment 'IP',
    port      char(5)      not null comment '端口',
    report    varchar(100) null,
    `default` int          not null,
    listen    int          not null,
    delay     int          not null comment '超时时间'
);

create table if not exists config
(
    name  varchar(256) not null comment '配置名',
    uid   char(10)     not null comment '群组',
    value varchar(500) not null comment '参数',
    primary key (name, uid)
);

create table if not exists update_time
(
    name varchar(255) not null primary key comment '插件名',
    time char(13)     not null comment '更新时间'
);
