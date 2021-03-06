import importlib
from pathlib import Path

from loguru import logger

_ignore = ['__init__.py', '__pycache__', 'loads.py', 'util.py']

for file in Path(__file__).parent.rglob(pattern='*.py'):
    try:
        if file.name not in _ignore and file.is_file():
            importlib.import_module(f'app.console.{file.parent.name}.{file.name.split(".")[0]}')
            logger.success(f'成功加载控制台插件: app.console.{file.parent.name}.{file.name.split(".")[0]}')
    except Exception as e:
        logger.error(e)

logger.success("控制台监听器启动成功")
