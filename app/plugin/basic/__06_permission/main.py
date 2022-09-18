from typing import Union

from arclet.alconna import Alconna, Args, Arpamar, Option, Subcommand
from graia.ariadne import Ariadne
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from graia.ariadne.model import Friend, Member
from loguru import logger

from app.core.commander import CommandDelegateManager
from app.core.config import Config
from app.core.settings import (
    ACTIVE_GROUP,
    ACTIVE_USER,
    ADMIN_USER,
    BANNED_USER,
    GROUP_ADMIN_USER,
    GROUP_PERM,
)
from app.entities.group import BotGroup
from app.entities.user import BotUser
from app.util.control import Permission
from app.util.phrases import args_error, not_admin, print_help, unknown_error

from .database.database import Group as DBGroup
from .database.database import User as DBUser

config: Config = Config()
manager: CommandDelegateManager = CommandDelegateManager()


@manager.register(
    entry="perm",
    brief_help="授权",
    alc=Alconna(
        command="perm",
        options=[
            Subcommand(
                "user",
                help_text="用户白名单",
                options=[
                    Option("--add|-a", args=Args["qq", [At, int]], help_text="用户加入白名单"),
                    Option("--delete|-d", args=Args["qq", [At, int]], help_text="用户移出白名单"),
                    Option("--list|-l", help_text="查看用户白名单"),
                ],
            ),
            Subcommand(
                "blacklist",
                help_text="用户黑名单",
                options=[
                    Option("--add|-a", args=Args["qq", [At, int]], help_text="用户加入黑名单"),
                    Option("--delete|-d", args=Args["qq", [At, int]], help_text="用户移出黑名单"),
                    Option("--list|-l", help_text="查看用户黑名单"),
                ],
            ),
            Subcommand(
                "group",
                help_text="群组白名单",
                options=[
                    Option("--add|-a", args=Args["group", int], help_text="群组加入白名单"),
                    Option("--delete|-d", args=Args["group", int], help_text="群组移出白名单"),
                    Option("--list|-l", help_text="查看群组白名单"),
                ],
            ),
            Option(
                "grant",
                help_text="调整用户权限等级(该功能操作者权限高于操作对象即可",
                args=Args["qq", [At, int]]["level", int],
            ),
        ],
        help_text="授权, 仅管理可用!",
    ),
)
async def process(app: Ariadne, target: Union[Friend, Member], command: Arpamar, alc: Alconna):
    user = command.subcommands.get("user")
    blacklist = command.subcommands.get("blacklist")
    group = command.subcommands.get("group")
    grant = command.options.get("grant")
    if all([not user, not blacklist, not group, not grant]):
        return await print_help(alc.get_help())
    try:
        if grant:
            if Permission.manual(target, 3):
                _target = grant["qq"].target if isinstance(grant["qq"], At) else grant["qq"]
                level = grant["level"]
                if target.id == target and level != 4 and Permission.manual(target, 4):
                    return MessageChain([Plain(f"怎么有master想给自己改权限呢？{config.BOT_NAME}很担心你呢，快去脑科看看吧！")])
                if await BotUser(_target).level == 0:
                    return MessageChain([Plain("在黑名单中的用户无法调整权限！若想调整其权限请先将其移出黑名单！")])
                if 1 <= level <= 2:
                    if result := await BotUser(_target).level:
                        if result == 4:
                            if Permission.manual(target, 4):
                                return MessageChain([Plain("就算是master也不能修改master哦！（怎么能有两个master呢")])
                            else:
                                return MessageChain([Plain("master level 不可更改！若想进行修改请直接修改配置文件！")])
                        elif result == 3:
                            if Permission.manual(target, 4):
                                ADMIN_USER.remove(target)
                                if level == 2:
                                    GROUP_ADMIN_USER.append(target)
                                return await grant_permission_process(_target, level)
                            else:
                                return MessageChain([Plain("权限不足，你必须达到等级4(master level)才可修改超级管理员权限！")])
                        elif result == 2:
                            if level == 1:
                                GROUP_ADMIN_USER.remove(target)
                            return await grant_permission_process(_target, level)
                        else:
                            if level == 2:
                                GROUP_ADMIN_USER.append(target)
                            return await grant_permission_process(_target, level)
                elif level == 3:
                    if Permission.manual(target, 4):
                        if target in GROUP_ADMIN_USER:
                            GROUP_ADMIN_USER.remove(_target)
                        ADMIN_USER.append(target)
                        return await grant_permission_process(_target, level)
                    else:
                        return MessageChain([Plain("权限不足，你必须达到等级4(master level)才可对超级管理员进行授权！")])
                else:
                    return MessageChain([Plain("level值非法！level值范围: 1-3\r\n1: user\r\n2: admin\r\n3: super admin")])
            else:
                return MessageChain([Plain("权限不足，爬!")])
        elif user:
            return await master_grant_user(app, target, user)
        elif blacklist:
            return await master_grant_blacklist(target, blacklist)
        elif group:
            return await master_grant_group(app, group, target)
        else:
            return args_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()


@Permission.require(level=Permission.SUPER_ADMIN)
async def master_grant_user(app: Ariadne, target: Union[Friend, Member], user_: dict):
    if add := user_.get("add"):
        _target = add["qq"].target if isinstance(add["qq"], At) else add["qq"]
        if Permission.compare(target, _target):
            BotUser(target, active=1)
            ACTIVE_USER.update({_target: "*"})
            return MessageChain([Plain("激活成功!")])
        return not_admin()
    elif delete := user_.get("delete"):
        _target = delete["qq"].target if isinstance(delete["qq"], At) else delete["qq"]
        if Permission.compare(target, _target):
            await BotUser(target, active=0).user_deactivate()
            if target in ACTIVE_USER:
                ACTIVE_USER.pop(target)
            return MessageChain([Plain("取消激活成功!")])
        return not_admin()
    elif user_.get("list"):
        msg = "用户白名单"
        if res := DBUser.select().where(DBUser.active == 1):
            friends = {i.id: i.nickname for i in await app.get_friend_list()}
            for qq in res:
                qq = int(qq.uid)
                if qq in friends.keys():
                    msg += f"\n{friends[qq]}: {qq}"
                else:
                    msg += f"\n未知用户昵称: {qq}"
        else:
            msg = "无激活用户"
        return MessageChain([Plain(msg)])


@Permission.require(level=Permission.SUPER_ADMIN)
async def master_grant_blacklist(target: Union[Friend, Member], blacklist: dict):
    if add := blacklist.get("add"):
        _target = add["qq"].target if isinstance(add["qq"], At) else add["qq"]
        if Permission.compare(target, _target):
            await BotUser(_target).grant_level(0)
            BANNED_USER.append(_target)
            return MessageChain([Plain("禁用成功!")])
        return not_admin()
    elif delete := blacklist.get("delete"):
        _target = delete["qq"].target if isinstance(delete["qq"], At) else delete["qq"]
        if Permission.compare(target, _target):
            await BotUser(_target).grant_level(1)
            if _target in BANNED_USER:
                BANNED_USER.remove(_target)
            return MessageChain([Plain("解除禁用成功!")])
        return not_admin()
    elif blacklist.get("list"):
        res = DBUser.select().where(DBUser.level == 0)
        return MessageChain([Plain("\r\n".join(qq.uid for qq in res) if res else "无黑名单用户")])


@Permission.require(level=Permission.SUPER_ADMIN)
async def master_grant_group(app: Ariadne, group: dict, _: Union[Friend, Member]):
    if add := group.get("add"):
        BotGroup(add["group"], active=1)
        ACTIVE_GROUP.update({add["group"]: "*"})
        return MessageChain([Plain("激活成功!")])
    elif delete := group.get("delete"):
        await BotGroup(delete["group"], active=0).group_deactivate()
        if delete["group"] in ACTIVE_GROUP:
            ACTIVE_GROUP.pop(delete["group"])
        return MessageChain([Plain("禁用成功!")])
    elif group.get("list"):
        msg = "群组白名单"
        if res := DBGroup.select().where(DBGroup.active == 1):
            groups = {i.id: {"name": i.name, "perm": i.account_perm.value} for i in await app.get_group_list()}
            for group_id in res:
                group_id = int(group_id.uid)
                if group_id in groups.keys():
                    msg += f"\n{groups[group_id]['name']}: {group_id} - {GROUP_PERM[groups[group_id]['perm']]}"
                else:
                    msg += f"\n未知群: {group_id} - 未加入该群"
        else:
            msg = "无白名单群组"
        return MessageChain([Plain(msg)])


async def grant_permission_process(user_id: int, new_level: int):
    """修改用户权限"""
    await BotUser(user_id).grant_level(new_level)
    return MessageChain([Plain(f"修改成功！\r\n{user_id} level: {new_level}")])
