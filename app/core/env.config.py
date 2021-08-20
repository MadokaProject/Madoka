# ============================示例配置文件=================================
# 使用需将其重命名为config.py，并填写修改其中的配置

# QQ账号基本配置
HOST = 'http://127.0.0.1:8080'  # 机器人mirai地址(str)
AUTHKEY = ''  # 机器人mirai验证密钥(str)
QQ = 'bot qq'  # 机器人QQ(str)

# 数据库基本配置
MYSQL_HOST = '127.0.0.1'  # 数据库地址(str)
MYSQL_PORT = 3306  # 数据库端口(int)
MYSQL_USER = 'root'  # 数据库用户名(str)
MYSQL_PWD = '123456'  # 数据库密码(str)
MYSQL_DB = 'qqbot'  # 数据库名(str)

# github仓库监听配置(监听仓库请通过指令配置)
REPO_GROUP = []  # 消息推送群聊(int)
REPO_TIME = '*/10  * * * *'  # 监听时间间隔(cron表达式)
