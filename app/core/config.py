import importlib
import json
import shutil
from pathlib import Path
from typing import Optional

import yaml
from loguru import logger
from pydantic import AnyHttpUrl, BaseSettings, Extra, validator

from app.util.tools import app_path, data_path


class MadokaInfo:
    NAME = "Madoka"
    VERSION = "4.3.1"
    DOCS = "https://madoka.colsrch.cn"
    REPO = "https://github.com/MadokaProject/Madoka"
    REMOTE_REPO_VERSION = "v4.3"
    REMOTE_VERSION_URL = "https://raw.fastgit.org/MadokaProject/Madoka/master/app/util/version.json"


class _Bot(BaseSettings, extra=Extra.ignore):
    account: int
    verify_key: str
    host: AnyHttpUrl = "http://127.0.0.1:8080"


class _Database(BaseSettings, extra=Extra.ignore):
    host: str = "127.0.0.1"
    port: int = 3306
    username: Optional[str]
    password: Optional[str]
    name: str
    type: str = "sqlite"

    @validator("type", always=True)
    def _check_type(cls, v, values):
        if v == "sqlite":
            if not values["name"].endswith(".db"):
                values["name"] += ".db"
            old_file = app_path("tmp/db", values["name"])
            if old_file.is_file():
                logger.warning("检测到旧的数据库文件，正在进行迁移: {} -> {}", old_file, data_path(values["name"]))
                old_file.rename(data_path(values["name"]))
            values["name"] = str(data_path(values["name"]))
            return v
        elif v == "mysql":
            try:
                if values["username"] and values["password"]:
                    return v
                raise KeyError
            except KeyError as e:
                raise ValueError("username or password is not set") from e
        raise ValueError("数据库类型不支持")


class _CoinSettings(BaseSettings, extra=Extra.ignore):
    name: str = "金币"


class _Github(BaseSettings, extra=Extra.ignore):
    enable: bool = False
    time: str = "*/10 * * * *"
    limit: int = 5
    token: str = None


class _Command(BaseSettings, extra=Extra.ignore):
    headers: list[str] = ["."]
    friend_limit: float = 0
    group_limit: float = 0

    @validator("friend_limit")
    def _friend_limit_validator(cls, v):
        if v < 0:
            logger.warning("好友限频小于0, 已自动设置为0")
            return 0
        return v

    @validator("group_limit")
    def _group_limit_validator(cls, v):
        if v < 0:
            logger.warning("群组限频小于0, 已自动设置为0")
            return 0
        return v


class _MessageQueue(BaseSettings, extra=Extra.ignore):
    limit: float = 1.5

    @validator("limit")
    def _limit_mq(cls, v):
        if v < 0:
            logger.warning("消息队列发送频率小于0, 已自动设置为0")
            return 0
        return v


class _Event(BaseSettings, extra=Extra.ignore):
    groupRecall2me: bool = True


class _BaiduAIModeration(BaseSettings, extra=Extra.ignore):
    app_id: Optional[str]
    api_key: Optional[str]
    secret_key: Optional[str]
    enable: bool = False

    @validator("enable", always=True)
    def _enable(cls, v, values):
        if v:
            try:
                if values["app_id"] and values["api_key"] and values["secret_key"]:
                    importlib.import_module("aip")
                    return v
                raise KeyError
            except KeyError as e:
                raise ValueError("app_id or api_key or secret_key is not set") from e
        return False


class _BaiduAI(BaseSettings, extra=Extra.ignore):
    moderation: _BaiduAIModeration


class _Config(BaseSettings, extra=Extra.ignore):
    bot: _Bot
    database: _Database
    coin_settings: _CoinSettings
    github: _Github
    command: _Command
    message_queue: _MessageQueue
    event: _Event
    baidu_ai: _BaiduAI
    name: str = "Madoka"
    master_qq: int
    master_name: str
    debug: bool = False
    online: bool = True

    def change_debug(self):
        if not self.online:
            return
        self.debug = not self.debug
        save_config()


class NoAliasDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True


def save_config():
    CONFIG_FILE.write_text(
        yaml.dump(json.loads(Config.json()), Dumper=NoAliasDumper, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


data_path().mkdir(parents=True, exist_ok=True)
CONFIG_FILE = data_path("config.yaml")
if not CONFIG_FILE.is_file():
    shutil.copy(Path(__file__).parent.joinpath("config.exp.yaml"), CONFIG_FILE)
    logger.warning(f"配置文件不存在，已自动生成，请修改配置文件后重启! - {CONFIG_FILE}")
    exit(1)
cf: dict = yaml.load(CONFIG_FILE.read_text("utf-8"), Loader=yaml.FullLoader)
try:
    Config = _Config.parse_obj(cf)
    if Config.database.type == "mysql":
        importlib.import_module("pymysql")
        DB_PARAMS = {
            "host": Config.database.host,
            "port": Config.database.port,
            "user": Config.database.username,
            "password": Config.database.password,
        }
    else:
        DB_PARAMS = {}
    old_plugin = app_path("plugin/plugin.json")
    if old_plugin.is_file():
        logger.warning("检测到旧的插件记录文件，正在进行迁移: {} -> {}", old_plugin, data_path("plugin.json"))
        old_plugin.rename(data_path("plugin.json"))
except ValueError as e:
    err_info = []
    pos_maxlen = 0
    for err in json.loads(e.json()):
        err_pos = ".".join(str(x) for x in err["loc"])
        err_msg = err["msg"]
        pos_maxlen = max(pos_maxlen, len(err_pos))
        err_info.append([err_pos, err_msg])
    logger.critical("以下配置项填写错误:")
    for err in err_info:
        logger.critical(f"{err[0].ljust(pos_maxlen)} => {err[1]}")
    logger.error("请检查配置文件上诉内容后尝试重新启动!")
    exit(1)
except ModuleNotFoundError as e:
    logger.error("依赖包缺少: %r" % e.name)
    if e.name == "pymysql":
        cmd = "pdm install -G mysql || pip install pymysql"
    elif e.name in ["aip", "chardet"]:
        cmd = "pdm install -G baidu || pip install baidu-aip"
    else:
        cmd = "重新安装依赖"
    logger.error("请尝试运行 '%s' 安装该依赖包后重新启动!" % cmd)
    exit(1)
except Exception as e:
    logger.exception(e)
    logger.critical("读取配置文件时发生未知错误，请检查配置文件是否填写正确")
    exit(1)
