import configparser
from pathlib import Path

from loguru import logger

from .exceptions import ConfigInitialized, ConfigAlreadyInitialized


class Config:
    INFO_NAME = 'Madoka'
    INFO_VERSION = '2.4.1'
    INFO_DOCS = 'https://madoka.colsrch.cn'
    INFO_REPO = 'https://github.com/MadokaProject/Madoka'
    REMOTE_REPO_VERSION = 'release'
    REMOTE_VERSION_URL = 'https://fastly.jsdelivr.net/gh/MadokaProject/Madoka@master/app/util/version.json'

    CONFIG_FILE = Path(__file__).parent.joinpath('config.ini')

    __instance = None
    __first_init: bool = False

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not self.__first_init:
            if not self.CONFIG_FILE.is_file():
                logger.error("配置文件未找到!")
                exit()
            self.cf = configparser.ConfigParser()
            self.cf.read(self.CONFIG_FILE, encoding='utf-8')
            try:
                self.LOGIN_HOST = self.cf.get('bot', 'host', fallback='127.0.0.1')
                self.LOGIN_PORT = self.cf.get('bot', 'port', fallback='8080')
                self.LOGIN_QQ = self.cf.getint('bot', 'qq')
                self.VERIFY_KEY = self.cf.get('bot', 'verify_key')
                self.BOT_NAME = self.cf.get('bot', 'bot_name')
                self.MASTER_QQ = self.cf.getint('bot', 'master_qq')
                self.MASTER_NAME = self.cf.get('bot', 'master_name')
                self.DEBUG = self.cf.getboolean('bot', 'debug', fallback=False)
                self.ONLINE = self.cf.getboolean('bot', 'online', fallback=True)
                self.HEARTBEAT_LOG = self.cf.getboolean('bot', 'heartbeat_log', fallback=False)

                self.MYSQL_HOST = self.cf.get('mysql', 'host', fallback='127.0.0.1')
                self.MYSQL_PORT = self.cf.getint('mysql', 'port', fallback=3306)
                self.MYSQL_USER = self.cf.get('mysql', 'user')
                self.MYSQL_PWD = self.cf.get('mysql', 'password')
                self.MYSQL_DATABASE = self.cf.get('mysql', 'database')

                self.COMMON_RETENTION = self.cf.get('log', 'commonRetention', fallback='7')
                self.ERROR_RETENTION = self.cf.get('log', 'errorRetention', fallback='30')

                self.COIN_NAME = self.cf.get('coin_settings', 'name', fallback='金币')

                self.REPO_ENABLE = self.cf.getboolean('github', 'enable', fallback=False)
                self.REPO_TIME = self.cf.get('github', 'time', fallback='*/10  * * * *')

                self.COMMAND_HEADERS = self.cf.get('command', 'headers', fallback='.').split()

                self.WEBSERVER_ENABLE = self.cf.getboolean('webserver', 'enable', fallback=False)
                self.WEBSERVER_HOST = self.cf.get('webserver', 'host', fallback='0.0.0.0')
                self.WEBSERVER_PORT = self.cf.get('webserver', 'port', fallback=8080)
                self.WEBSERVER_DEBUG = self.cf.getboolean('webserver', 'debug', fallback=False)

                self.EVENT_GROUP_RECALL = self.cf.getboolean('event', 'groupRecall2me', fallback=True)
            except configparser.NoOptionError as e:
                logger.error("配置项缺失: 没有在 %r 中找到 %r" % (e.section, e.option))
                logger.error("请检查配置项后尝试重新启动!")
                exit()
        else:
            raise ConfigAlreadyInitialized()

    @classmethod
    def get_instance(cls):
        if cls.__instance:
            return cls.__instance
        else:
            raise ConfigInitialized()

    def change_debug(self):
        if not self.ONLINE:
            return
        if self.DEBUG:
            self.cf.set('bot', 'debug', 'false')
            self.DEBUG = False
        else:
            self.cf.set('bot', 'debug', 'true')
            self.DEBUG = True
        with open(self.CONFIG_FILE, 'w+') as fb:
            self.cf.write(fb)
