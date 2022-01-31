import configparser
import os

from app.util.tools import app_path


class Config:
    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.cf.read(os.sep.join([app_path(), 'core', 'config.ini']), encoding='utf-8')

        self.INFO_NAME = 'Madoka'
        self.INFO_VERSION = '2.0.0-rc3'
        self.INFO_DOCS = 'https://madoka.colsrch.cn'
        self.INFO_REPO = 'https://github.com/MadokaProject/Madoka'

        self.LOGIN_HOST = self.cf.get('bot', 'host', fallback='127.0.0.1')
        self.LOGIN_PORT = self.cf.get('bot', 'port', fallback='8080')
        self.LOGIN_QQ = self.cf.get('bot', 'qq')
        self.VERIFY_KEY = self.cf.get('bot', 'verify_key')
        self.BOT_NAME = self.cf.get('bot', 'bot_name')
        self.MASTER_QQ = self.cf.get('bot', 'master_qq')
        self.MASTER_NAME = self.cf.get('bot', 'master_name')
        self.DEBUG = True if self.cf.get('bot', 'debug', fallback='False').lower() == 'true' else False
        self.ONLINE = True if self.cf.get('bot', 'online', fallback='True').lower() == 'true' else False
        self.HEARTBEAT_LOG = False if self.cf.get('bot', 'heartbeat_log', fallback='False').lower() == 'false' else True

        self.MYSQL_HOST = self.cf.get('mysql', 'host', fallback='127.0.0.1')
        self.MYSQL_PORT = self.cf.getint('mysql', 'port', fallback=3306)
        self.MYSQL_USER = self.cf.get('mysql', 'user')
        self.MYSQL_PWD = self.cf.get('mysql', 'password')
        self.MYSQL_DATABASE = self.cf.get('mysql', 'database')

        self.COMMON_RETENTION = self.cf.get('log', 'commonRetention', fallback='7')
        self.ERROR_RETENTION = self.cf.get('log', 'errorRetention', fallback='30')

        self.COIN_NAME = self.cf.get('coin_settings', 'name', fallback='金币')

        self.REPO_ENABLE = True if self.cf.get('github', 'enable', fallback='False').lower() == 'true' else False
        self.REPO_TIME = self.cf.get('github', 'time', fallback='*/10  * * * *')

    def change_debug(self):
        if not self.ONLINE:
            return
        if self.DEBUG:
            self.cf.set('bot', 'debug', 'false')
            self.DEBUG = False
        else:
            self.cf.set('bot', 'debug', 'true')
            self.DEBUG = True
        with open(os.sep.join([app_path(), 'core', 'config.ini']), 'w+') as fb:
            self.cf.write(fb)
