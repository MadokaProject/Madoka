import pickle
from datetime import datetime, timedelta

import aiohttp.client
from loguru import logger

from app.core.app import AppCore
from app.core.config import Config
from app.core.settings import REPO
from app.util.alconna import Args, Arpamar, Commander, Option, Subcommand
from app.util.control import Permission
from app.util.graia import GraiaScheduler, Group, GroupMessage, Plain, message, timers
from app.util.network import general_request
from app.util.online_config import save_config
from app.util.phrases import args_error
from app.util.tools import app_path

core: AppCore = AppCore()
config: Config = Config()
app = core.get_app()
sche: GraiaScheduler = core.get_scheduler()
command = Commander(
    "github",
    "Github监听",
    Subcommand(
        "add",
        help_text="添加监听仓库",
        args=Args["repo", str]["api", str, "project/repo"],
        options=[Option("--branch|-b", args=Args["branch", str, "*"], help_text="指定监听的分支,使用 , 分隔, 默认监听全部分支")],
    ),
    Subcommand(
        "modify",
        help_text="修改监听仓库配置",
        args=Args["repo", str],
        options=[
            Option("--name|-n", args=Args["name", str], help_text="修改仓库名"),
            Option("--api|-a", args=Args["api", str, "project/repo"], help_text="修改监听API"),
            Option("--branch|-b", args=Args["branch", str, "*"], help_text="修改监听的分支, 使用 , 分隔, *: 监听所有分支"),
        ],
    ),
    Option("remove", help_text="删除监听仓库", args=Args["repo", str]),
    Option("list", help_text="列出当前群组所有监听仓库"),
    help_text="Github 监听, 仅管理可用",
)


@command.parse("add", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def add(sender: Group, cmd: Arpamar):
    branch = cmd.query("branch").replace("，", ",").split(",") if cmd.find("branch") else ["*"]
    group_id = str(sender.id)
    if group_id in REPO and cmd.query("repo") in REPO[group_id]:
        return message("添加失败，该仓库名已存在!").target(sender).send()
    if cmd.query("api") == "project/repo":
        return message("添加失败，监听仓库不能为空!").target(sender).send()
    repo_info = {
        cmd.query("repo"): {
            "api": f"https://api.github.com/repos/{add['api'].strip('/')}/branches",
            "branch": branch,
        }
    }
    await save_config("repo", sender, repo_info, model="add")
    if group_id not in REPO:
        REPO[group_id] = repo_info
    else:
        REPO[group_id].update(repo_info)
    return message("添加成功!").target(sender).send()


@command.parse("modify", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def modify(sender: Group, cmd: Arpamar):
    group_id = str(sender.id)
    repo = cmd.query("repo")
    _name = cmd.query("name")
    _api = cmd.query("api")
    _branch = cmd.query("branch")
    if all([not _name, not _api, not _branch]):
        return args_error(sender)
    if group_id not in REPO or repo not in REPO[group_id]:
        return message("修改失败，该仓库名不存在!").target(sender).send()
    if _name:
        await save_config("repo", sender, repo, model="remove")
        await save_config("repo", sender, {_name: REPO[group_id][repo]}, model="add")
        REPO[group_id][_name] = REPO[group_id].pop(repo)
        repo = _name
    if _api:
        if _api == "project/repo":
            return message("修改失败，监听仓库不能为空!").target(sender).send()
        _api = f"https://api.github.com/repos/{_api.strip('/')}/branches"
        REPO[group_id][repo]["api"] = _api
        await save_config("repo", sender, {repo: REPO[group_id][repo]}, model="add")
    if _branch:
        REPO[group_id][repo]["branch"] = _branch.replace("，", ",").split(",")
        await save_config("repo", sender, {repo: REPO[group_id][repo]}, model="add")
    return message("修改成功!").target(sender).send()


@command.parse("remove", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def remove(sender: Group, cmd: Arpamar):
    group_id = str(sender.id)
    repo = cmd.query("repo")
    if group_id not in REPO or repo not in REPO[group_id]:
        return message("删除失败，该仓库名不存在!").target(sender).send()
    await save_config("repo", sender, repo, model="remove")
    REPO[group_id].pop(repo)
    return message("删除成功!").target(sender).send()


@command.parse("list", events=[GroupMessage], permission=Permission.GROUP_ADMIN)
async def list(sender: Group):
    if str(sender.id) in REPO:
        return (
            message(
                "\r\n".join(
                    f"{name}: \r\napi: {info['api']}\r\nbranch: {info['branch']}"
                    for name, info in REPO[str(sender.id)].items()
                )
            )
            .target(sender)
            .send()
        )
    return message("该群组未配置Github监听仓库！").target(sender).send()


@sche.schedule(timers.crontabify(config.REPO_TIME))
@logger.catch
async def tasker():
    if not config.ONLINE:  # 非 ONLINE 模式不监听仓库
        return
    if not config.REPO_ENABLE:  # 未开启仓库监听
        return
    logger.info("github_listener is running...")

    app_path().joinpath("tmp/github").mkdir(parents=True, exist_ok=True)
    for group in REPO.keys():
        file = app_path().joinpath(f"tmp/github/{group}.dat")
        if file.exists():
            with open(file, "rb") as f:
                obj = pickle.load(f)
        else:
            obj = {}
        for name, info in REPO[group].items():
            if not obj.__contains__(name):
                obj.update({name: {}})
            try:
                branches = await general_request(info["api"], "get", "JSON")
                for branch in branches:
                    if info["branch"][0] != "*" and branch["name"] not in info["branch"]:
                        continue
                    if not obj[name].__contains__(branch["name"]):
                        obj[name].update({branch["name"]: None})
                    if branch["commit"]["sha"] != obj[name][branch["name"]]:
                        obj[name][branch["name"]] = branch["commit"]["sha"]
                        await message_push(group, name, branch)
            except aiohttp.client.ClientConnectorError:
                logger.warning(f"获取仓库信息超时 - {info['api']}")
            except Exception as e:
                logger.exception(f"获取仓库信息失败 - {e}")
        with open(file, "wb") as f:
            pickle.dump(obj, f)


async def message_push(group, repo, branch):
    commit_info = await general_request(branch["commit"]["url"], _type="JSON")
    commit_time = datetime.strftime(
        datetime.strptime(commit_info["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8),
        "%Y-%m-%d %H:%M:%S",
    )
    message(
        [
            Plain(f"Recent Commits to {repo}: {branch['name']}"),
            Plain(f"\nCommit: {commit_info['commit']['message']}"),
            Plain(f"\nAuthor: {commit_info['commit']['author']['name']}"),
            Plain(f"\nUpdated: {commit_time}"),
            Plain(f"\nLink: {commit_info['html_url']}"),
        ]
    ).target(group).send()
