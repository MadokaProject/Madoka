from app.util.dao import MysqlDao


def auto_create_sql():
    try:
        with MysqlDao() as db:
            db.update(
                "create table if not exists msg( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(10) null comment '群号', \
                    qid char(12) null comment 'QQ', \
                    datetime datetime not null comment '时间', \
                    content varchar(800) not null comment '内容')"
            )
            db.update(
                "create table if not exists friend_listener( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) null comment 'QQ', \
                    permission char not null comment '许可', \
                    active int not null comment '用户', \
                    admin int not null comment '管理')"
            )
            db.update(
                "create table if not exists group_listener( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) null comment '群号', \
                    permission char not null comment '许可')"
            )
            db.update(
                "create table if not exists group_reply( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) not null comment '群号', \
                    keyword varchar(50) not null comment '关键词', \
                    text varchar(100) not null comment '回复消息')"
            )
            db.update(
                "create table if not exists github( \
                    id int auto_increment comment '序号' primary key, \
                    repo varchar(50) not null comment '仓库', \
                    branch varchar(50) not null comment '分支', \
                    sha char(40) not null comment '记录')"
            )
            db.update(
                "create table if not exists github_config( \
                    id int auto_increment comment '序号' primary key, \
                    repo char(50) not null comment '仓库名', \
                    api char(110) not null comment 'api')"
            )
            db.update(
                "create table if not exists group_join( \
                    id int auto_increment comment '序号' primary key, \
                    uid char(12) not null comment '群号', \
                    text varchar(200) not null comment '欢迎消息', \
                    active int not null comment '开关')"
            )
            db.update(
                "create table if not exists mc_server( \
                    ip char(15) not null comment 'IP', \
                    port char(5) not null comment '端口', \
                    report varchar(100) null, \
                    `default` int not null, \
                    listen int not null, \
                    delay int not null comment '超时时间')"
            )
            print('初始化数据库成功！')
    except Exception as e:
        print('初始化数据库失败：' + str(e))
