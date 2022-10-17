import configparser

import yaml
from loguru import logger

from app.util.tools import app_path, data_path

OLD_CONFIG_FILE = app_path("core/config.ini")
CONFIG_FILE = data_path("config.yaml")

if OLD_CONFIG_FILE.is_file():
    cf = configparser.ConfigParser()
    cf.read(OLD_CONFIG_FILE, encoding="utf-8")
    config_json: dict = {
        "name": cf.get("bot", "bot_name", fallback=None),
        "master_qq": cf.getint("bot", "master_qq", fallback=None),
        "master_name": cf.get("bot", "master_name", fallback=None),
        "debug": cf.getboolean("bot", "debug", fallback=False),
        "online": cf.getboolean("bot", "online", fallback=True),
        "bot": {
            "host": f"http://{cf.get('bot', 'host', fallback='127.0.0.1')}:{cf.getint('bot', 'port', fallback=8080)}",
            "account": cf.getint("bot", "qq", fallback=None),
            "verify_key": cf.get("bot", "verify_key", fallback=None),
        },
        "database": {
            "type": cf.get("database", "type", fallback="sqlite"),
            "name": cf.get("database", "name", fallback=None),
            "host": cf.get("database", "host", fallback="localhost"),
            "port": cf.getint("database", "port", fallback=3306),
            "username": cf.get("database", "user", fallback=None),
            "password": cf.get("database", "password", fallback=None),
        },
        "coin_settings": {"name": cf.get("coin_settings", "name", fallback="金币")},
        "github": {
            "enable": cf.getboolean("github", "enable", fallback=False),
            "time": cf.get("github", "time", fallback="*/10 * * * *"),
        },
        "command": {
            "headers": cf.get("command", "headers", fallback=".").split(),
            "friend_limit": cf.getfloat("command", "friend_limit", fallback=0),
            "group_limit": cf.getfloat("command", "group_limit", fallback=0),
        },
        "message_queue": {"limit": cf.getfloat("message_queue", "limit", fallback=1.5)},
        "event": {"groupRecall2me": cf.getboolean("event", "groupRecall2me", fallback=True)},
    }
    logger.success("配置文件转换成功")
    CONFIG_FILE.write_text(yaml.dump(config_json, allow_unicode=True, sort_keys=False), encoding="utf-8")
    logger.success(f"{OLD_CONFIG_FILE} => {CONFIG_FILE}")

logger.success("迁移成功！")
