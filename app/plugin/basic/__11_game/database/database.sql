create table if not exists game
(
    uuid             char(36)      not null comment 'UUID',
    qid              char(12)      not null comment 'QQ号',
    consecutive_days int default 0 not null comment '连续签到天数',
    total_days       int default 0 not null comment '累计签到天数',
    last_signin_time date comment '上次签到时间',
    auto_signin      int default 0 not null comment '自动签到',
    coin             int comment '今日获得货币',
    coins            int default 0 not null comment '货币',
    intimacy         int default 0 not null comment '好感度',
    intimacy_level   int default 0 not null comment '好感度等级',
    english_answer   int default 0 comment '英语答题榜',
    primary key (uuid, qid)
);
