import configparser
import importlib
from pathlib import Path

from loguru import logger

from app.util.decorator import Singleton
from app.util.tools import app_path


class Config(metaclass=Singleton):
    INFO_NAME = "Madoka"
    INFO_VERSION = "3.3.0"
    INFO_DOCS = "https://madoka.colsrch.cn"
    INFO_REPO = "https://github.com/MadokaProject/Madoka"
    REMOTE_REPO_VERSION = "release"
    REMOTE_VERSION_URL = "https://fastly.jsdelivr.net/gh/MadokaProject/Madoka@master/app/util/version.json"

    CONFIG_FILE = Path(__file__).parent.joinpath("config.ini")

    def __init__(self):
        if not self.CONFIG_FILE.is_file():
            logger.error("配置文件未找到!")
            exit()
        self.cf = configparser.ConfigParser()
        self.cf.read(self.CONFIG_FILE, encoding="utf-8")
        try:
            self.LOGIN_HOST = self.cf.get("bot", "host", fallback="127.0.0.1")
            self.LOGIN_PORT = self.cf.get("bot", "port", fallback="8080")
            self.LOGIN_QQ = self.cf.getint("bot", "qq")
            self.VERIFY_KEY = self.cf.get("bot", "verify_key")
            self.BOT_NAME = self.cf.get("bot", "bot_name")
            self.MASTER_QQ = self.cf.getint("bot", "master_qq")
            self.MASTER_NAME = self.cf.get("bot", "master_name")
            self.DEBUG = self.cf.getboolean("bot", "debug", fallback=False)
            self.ONLINE = self.cf.getboolean("bot", "online", fallback=True)
            self.HEARTBEAT_LOG = self.cf.getboolean("bot", "heartbeat_log", fallback=False)

            self.DB_TYPE = self.cf.get("database", "type", fallback="sqlite")
            if self.DB_TYPE not in ("sqlite", "mysql"):
                raise ValueError("database", "type")
            self.DB_NAME = self.cf.get("database", "name")
            if self.DB_TYPE == "mysql":
                importlib.import_module("pymysql")

                self.DB_PARAMS = {
                    "host": self.cf.get("database", "host", fallback="localhost"),
                    "port": self.cf.getint("database", "port", fallback=3306),
                    "user": self.cf.get("database", "user"),
                    "password": self.cf.get("database", "password"),
                }
            else:
                importlib.import_module("sqlite3")

                self.DB_PARAMS = {}
                if not self.DB_NAME.endswith(".db"):
                    self.DB_NAME += ".db"
                app_path("tmp/db").mkdir(parents=True, exist_ok=True)
                self.DB_NAME = str(app_path("tmp/db", self.DB_NAME))

            self.COIN_NAME = self.cf.get("coin_settings", "name", fallback="金币")

            self.REPO_ENABLE = self.cf.getboolean("github", "enable", fallback=False)
            self.REPO_TIME = self.cf.get("github", "time", fallback="*/10  * * * *")

            self.COMMAND_HEADERS = self.cf.get("command", "headers", fallback=".").split()

            self.WEBSERVER_ENABLE = self.cf.getboolean("webserver", "enable", fallback=False)
            self.WEBSERVER_HOST = self.cf.get("webserver", "host", fallback="0.0.0.0")
            self.WEBSERVER_PORT = self.cf.get("webserver", "port", fallback=8080)
            self.WEBSERVER_DEBUG = self.cf.getboolean("webserver", "debug", fallback=False)

            self.EVENT_GROUP_RECALL = self.cf.getboolean("event", "groupRecall2me", fallback=True)
        except ValueError as e:
            logger.error("配置项错误: %r 中的 %r 参数错误!" % (e.args[0], e.args[1]))
            logger.error("请检查配置项后尝试重新启动!")
            exit()
        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            if hasattr(e, "option"):
                logger.error("配置项缺失: 没有在 %r 中找到 %r" % (e.section, e.option))
            else:
                logger.error("配置项缺失: 没有找到 %r " % e.section)
            logger.error("请检查配置项后尝试重新启动!")
            exit()
        except ModuleNotFoundError as e:
            logger.error("依赖包缺少: %r" % e.name)
            cmd = "pip install pymysql" if e.name == "pymysql" else "pip install pysqlite3"
            logger.error("请尝试运行 '%s' 安装该依赖包后重新启动!" % cmd)
            exit()

    def change_debug(self):
        if not self.ONLINE:
            return
        if self.DEBUG:
            self.cf.set("bot", "debug", "false")
            self.DEBUG = False
        else:
            self.cf.set("bot", "debug", "true")
            self.DEBUG = True
        with open(self.CONFIG_FILE, "w+") as fb:
            self.cf.write(fb)
