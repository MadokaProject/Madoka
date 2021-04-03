import pymysql
from app.core.config import *

# 建立数据库连接
conn = pymysql.connect(
    host=MYSQL_HOST,
    port=MYSQL_PORT,
    user=MYSQL_USER,
    password=MYSQL_PWD,
    db=MYSQL_DB,
    charset='utf8'
)


def create(name):  # 创建数据表
    if find_table(name) == 0:
        # 创建数据库对象
        db = conn.cursor()
        sql = "create table %s(\
        id int not null auto_increment primary key comment '序号',\
        instruction varchar(30) not null comment '指令',\
        type char(5) not null comment '类型',\
        reply varchar(100) not null comment '答复'\
        ) engine=InnoDB;" % name
        db.execute(sql)
        db.close()
        if find_table(name) == 1:
            return 1  # 数据表创建成功
        else:
            return 0  # 数据表创建失败
    else:
        return -1  # 数据表已存在


def create_record(name):  # 创建聊天记录数据表
    if find_table(name) == 0:
        # 创建数据库对象
        db = conn.cursor()
        sql = "create table %s(\
        id int not null auto_increment primary key comment '序号',\
        qq varchar(13) not null comment 'QQ',\
        datetime char(19) not null comment '时间',\
        content varchar(500) not null comment '内容'\
        ) engine=InnoDB;" % name
        db.execute(sql)
        db.close()
        if find_table(name) == 1:
            return 1  # 数据表创建成功
        else:
            return 0  # 数据表创建失败
    else:
        return -1  # 数据表已存在


def insert_record(name, qq, datetime, content):  # 添加内容
    # 创建数据库对象
    db = conn.cursor()
    sql = "insert into %s(qq,datetime,content) values('%s','%s','%s');" % (name, qq, datetime, content)
    db.execute(sql)
    conn.commit()
    db.close()


def find(name):  # 查找数据表内容
    # 创建数据库对象
    db = conn.cursor()
    # 写入SQL语句
    sql = "select * from %s " % name
    # 执行sql命令
    db.execute(sql)
    # 获取一个查询
    # result = db.fetchone()
    # 获取全部的查询内容
    result = db.fetchall()
    # 关闭链接
    db.close()
    return result


def record_find(name, qq):  # 查找指定人的历史消息
    db = conn.cursor()
    sql = "SELECT * FROM %s WHERE qq = %s" % (name, qq)
    db.execute(sql)
    result = db.fetchall()
    db.close()
    return result[-3:]


def find_table(table_name):  # 查找数据表
    # 创建数据库对象
    db = conn.cursor()
    sql = "show tables from qqbot"
    db.execute(sql)
    result = db.fetchall()
    db.close()
    for table in result:
        if table[0] == table_name:  # 数据表存在
            return 1
    else:  # 数据表不存在
        return 0


def insert(name, instruction, type_insert, reply):  # 添加内容
    target = find(name)
    if target:
        for i in find(name):
            if i[1] == instruction:
                return -1  # 要添加指令已存在
    # 创建数据库对象
    db = conn.cursor()
    sql = "insert into %s(instruction,type,reply) values('%s','%s','%s');" % (name, instruction, type_insert, reply)
    db.execute(sql)
    conn.commit()
    db.close()
    for i in find(name):
        if i[1] == instruction:
            return 1  # 指令添加成功
    else:
        return 0


def github_create(repo):
    if find_table(repo) == 0:
        # 创建数据库对象
        db = conn.cursor()
        sql = "CREATE TABLE %s(\
        id int not null auto_increment primary key comment '序号',\
        branch varchar(50) not null COMMENT '分支',\
        sha char(40) not null COMMENT '记录'\
        )ENGINE=InnoDB;" % repo
        db.execute(sql)
        db.close()
        if find_table(repo) == 1:
            return 1  # 数据表创建成功
        else:
            return 0  # 数据表创建失败
    else:
        return -1  # 数据表已存在


def github_find(repo):  # github仓库检测
    # 创建数据库对象
    db = conn.cursor()
    # 写入SQL语句
    sql = "select * from %s " % repo
    # 执行sql命令
    db.execute(sql)
    # 获取一个查询
    # result = db.fetchone()
    # 获取全部的查询内容
    result = db.fetchall()
    # 关闭链接
    db.close()
    return result


def github_update(repo, branch, sha):  # github数据表更新
    db = conn.cursor()
    sql = "update %s set sha = '%s' where branch = '%s'" % (repo, sha, branch)
    db.execute(sql)
    conn.commit()
    db.close()


def github_insert(repo, branch, sha):  # 插入内容
    # 创建数据库对象
    db = conn.cursor()
    sql = "insert into %s(branch,sha) values('%s','%s');" % (repo, branch, sha)
    db.execute(sql)
    conn.commit()
    db.close()