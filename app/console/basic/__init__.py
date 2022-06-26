import importlib

from loguru import logger
from pathlib import Path


for file in Path(__file__).parent.rglob(pattern='*.py'):
    if file.name not in ["__init__.py", "__pycache__"] and file.is_file():
        importlib.import_module(f'app.console.basic.{file.parent.name}.{file.name.split(".")[0]}')
        logger.success(f'成功加载控制台插件: app.console.basic.{file.parent.name}.{file.name.split(".")[0]}')
