# ============================示例配置文件=================================
# 使用需将其重命名为config.py，并填写修改其中的配置

# QQ账号基本配置
HOST = 'http://example:port'  # 机器人mirai地址(str)
AUTHKEY = ''  # 机器人mirai验证密钥(str)
QQ = 'bot qq'  # 机器人QQ(str)

# 数据库基本配置
MYSQL_HOST = '127.0.0.1'  # 数据库地址(str)
MYSQL_PORT = 3306  # 数据库端口(int)
MYSQL_USER = 'root'  # 数据库用户名(str)
MYSQL_PWD = '123456'  # 数据库密码(str)
MYSQL_DB = 'qqbot'  # 数据库名(str)

# 变量配置
ADMIN_USER = [123456]  # 管理员(int)
ACTIVE_USER = [123456]  # 监听好友(int)
ACTIVE_GROUP = {123456: '*', 1234567: '*'}  # 监听群聊：前者为群号，后者为指令权限许可范围（ - 、* 、[qid]）(keys.int,values.str)

# github仓库监听配置
REPO_GROUP = []  # 消息推送群聊(int)
REPO_TIME = 15  # 监听时间间隔(int)
REPO_NAME = []  # 仓库名(str)
REPO_API = []  # 仓库api（个数须与REPO_NAME对应）(str)
