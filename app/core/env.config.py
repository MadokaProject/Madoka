# ============================示例配置文件=================================
# 使用需将其重命名为config.py，并填写修改其中的配置

# QQ账号基本配置
HOST = 'http://example:port'  # 机器人mirar地址
AUTHKEY = ''  # 机器人验证密钥
QQ = 'bot qq'  # 机器人QQ

# 数据库基本配置
MYSQL_HOST = '127.0.0.1'  # 数据库地址
MYSQL_PORT = 3306  # 数据库端口
MYSQL_USER = 'root'  # 数据库用户名
MYSQL_PWD = '123456'  # 数据库密码
MYSQL_DB = 'qqbot'  # 数据库名

# 变量配置
ADMIN_USER = [123456]  # 管理员
ACTIVE_USER = [123456]  # 监听好友
ACTIVE_GROUP = {123456: '*', 1234567: '*'}  # 监听群聊：前者为群号，后者为指令可用范围（ - 、* 、[qid]）

# github仓库监听配置
REPO_TIME = 15  # 监听时间间隔
REPO_NAME = []  # 仓库名
REPO_API = []  # 仓库api（个数须与REPO_NAME对应）
