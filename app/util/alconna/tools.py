from arclet.alconna import Namespace, config

from app.core.config import Config

config.namespaces["plugin"] = Namespace(name="plugin", headers=Config.command.headers)
config.namespaces["console"] = Namespace(name="console", fuzzy_match=True)


def set_default_namespace(name: str, **kwargs):
    config.default_namespace = Namespace(name=name, **kwargs) if kwargs else name
