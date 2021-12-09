import configparser
import os

from app.util.tools import app_path


class Config:
    def __init__(self):
        self.cf = configparser.ConfigParser()
        self.cf.read(os.sep.join([app_path(), 'core', 'config.ini']), encoding='utf-8')

        self.LOGIN_HOST = self.cf.get('bot', 'login_host', fallback='127.0.0.1')
        self.LOGIN_PORT = self.cf.get('bot', 'login_port', fallback='8080')
        self.LOGIN_QQ = self.cf.get('bot', 'login_qq')
        self.AUTH_KEY = self.cf.get('bot', 'auth_key')
        self.BOT_NAME = self.cf.get('bot', 'bot_name')
        self.MASTER_QQ = self.cf.get('bot', 'master_qq')
        self.DEBUG = True if self.cf.get('bot', 'debug', fallback='False').lower() == 'true' else False
        self.ONLINE = True if self.cf.get('bot', 'online', fallback='True').lower() == 'true' else False

        self.MYSQL_HOST = self.cf.get('mysql', 'mysql_host', fallback='127.0.0.1')
        self.MYSQL_PORT = self.cf.getint('mysql', 'mysql_port', fallback=3306)
        self.MYSQL_USER = self.cf.get('mysql', 'mysql_user')
        self.MYSQL_PWD = self.cf.get('mysql', 'mysql_pwd')
        self.MYSQL_DATABASE = self.cf.get('mysql', 'mysql_database')

        self.REPO_ENABLE = True if self.cf.get('github', 'enable', fallback='False').lower() == 'true' else False
        self.REPO_GROUP = self.cf.get('github', 'repo_group', fallback='[]').strip('[').strip(']').split(',')
        self.REPO_TIME = self.cf.get('github', 'repo_time', fallback='*/10  * * * *')

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
