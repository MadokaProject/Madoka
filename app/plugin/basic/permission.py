from typing import Union

from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain, At
from loguru import logger

from app.core.command_manager import CommandManager
from app.core.settings import *
from app.entities.group import BotGroup
from app.entities.user import BotUser
from app.plugin.base import Plugin, InitDB
from app.util.control import Permission
from app.util.dao import MysqlDao
from app.util.decorator import permission_required


class Module(Plugin):
    entry = 'perm'
    brief_help = '授权'
    manager: CommandManager = CommandManager.get_command_instance()

    @manager(Alconna(
        headers=manager.headers,
        command=entry,
        options=[
            Subcommand('user', help_text='用户白名单', options=[
                Option('--add', alias='-a', args=Args['qq': Union[At, int]], help_text='用户加入白名单'),
                Option('--delete', alias='-d', args=Args['qq': Union[At, int]], help_text='用户移出白名单'),
                Option('--list', alias='-l', help_text='查看用户白名单')
            ]),
            Subcommand('blacklist', help_text='用户黑名单', options=[
                Option('--add', alias='-a', args=Args['qq': Union[At, int]], help_text='用户加入黑名单'),
                Option('--delete', alias='-d', args=Args['qq': Union[At, int]], help_text='用户移出黑名单'),
                Option('--list', alias='-l', help_text='查看用户黑名单')
            ]),
            Subcommand('group', help_text='群组白名单', options=[
                Option('--add', alias='-a', args=Args['group': int], help_text='群组加入白名单'),
                Option('--delete', alias='-d', args=Args['group': int], help_text='群组移出白名单'),
                Option('--list', alias='-l', help_text='查看群组白名单')
            ]),
            Subcommand('grant', help_text='调整用户权限等级', args=Args['qq': Union[At, int], 'level': int])
        ],
        help_text='授权, 仅管理可用!'
    ))
    async def process(self, command: Arpamar, alc: Alconna):
        subcommand = command.subcommands
        other_args = command.other_args
        if not subcommand:
            return await self.print_help(alc.get_help())
        try:
            if subcommand.__contains__('grant'):
                if Permission.require(self.member if hasattr(self, 'group') else self.friend, 3):
                    user = self.member if hasattr(self, 'group') else self.friend
                    target = other_args['qq'].target if isinstance(other_args['qq'], At) else other_args['qq']
                    level = other_args['level']
                    if user.id == target and level != 4 and Permission.require(user, 4):
                        return MessageChain.create([Plain(f'怎么有master想给自己改权限呢？{Config().BOT_NAME}很担心你呢，快去脑科看看吧！')])
                    if await BotUser(target).get_level() == 0:
                        return MessageChain.create([Plain('在黑名单中的用户无法调整权限！若想调整其权限请先将其移出黑名单！')])
                    if 1 <= level <= 2:
                        if result := await BotUser(target).get_level():
                            if result == 4:
                                if Permission.require(user, 4):
                                    return MessageChain.create([Plain('就算是master也不能修改master哦！（怎么能有两个master呢')])
                                else:
                                    return MessageChain.create([Plain('master level 不可更改！若想进行修改请直接修改配置文件！')])
                            elif result == 3:
                                if Permission.require(user, 4):
                                    await self.grant_permission_process(target, level)
                                    ADMIN_USER.remove(target)
                                    if level == 2:
                                        GROUP_ADMIN_USER.append(target)
                                else:
                                    return MessageChain.create([Plain("权限不足，你必须达到等级4(master level)才可修改超级管理员权限！")])
                            elif result == 2:
                                await self.grant_permission_process(target, level)
                                if level == 1:
                                    GROUP_ADMIN_USER.remove(target)
                            else:
                                await self.grant_permission_process(target, level)
                                if level == 2:
                                    GROUP_ADMIN_USER.append(target)
                    elif level == 3:
                        if Permission.require(user, 4):
                            await self.grant_permission_process(target, level)
                            if target in GROUP_ADMIN_USER:
                                GROUP_ADMIN_USER.remove(target)
                            ADMIN_USER.append(target)
                        else:
                            return MessageChain.create([Plain('权限不足，你必须达到等级4(master level)才可对超级管理员进行授权！')])
                    else:
                        return MessageChain.create([
                            Plain('level值非法！level值范围: 1-3\r\n1: user\r\n2: admin\r\n3: super admin')
                        ])
                else:
                    return MessageChain.create([Plain('权限不足，爬!')])
            elif subcommand:
                return await self.master_grant(subcommand, other_args)
            return self.args_error()
        except Exception as e:
            logger.exception(e)
            return self.unkown_error()

    @permission_required(level=Permission.SUPER_ADMIN)
    async def master_grant(self, subcommand, other_args):
        if subcommand.__contains__('user'):
            if subcommand['user'].__contains__('add'):
                target = other_args['qq'].target if isinstance(other_args['qq'], At) else other_args['qq']
                if Permission.compare(self.member if hasattr(self, 'group') else self.friend, target):
                    BotUser(target, active=1)
                    ACTIVE_USER.update({target: '*'})
                    return MessageChain.create([Plain('激活成功!')])
                return self.not_admin()
            elif subcommand['user'].__contains__('delete'):
                target = other_args['qq'].target if isinstance(other_args['qq'], At) else other_args['qq']
                if Permission.compare(self.member if hasattr(self, 'group') else self.friend, target):
                    await BotUser(target, active=0).user_deactivate()
                    if target in ACTIVE_USER:
                        ACTIVE_USER.pop(target)
                    return MessageChain.create([Plain('取消激活成功!')])
                return self.not_admin()
            elif subcommand['user'].__contains__('list'):
                with MysqlDao() as db:
                    res = db.query("SELECT uid FROM user WHERE active=1")
                msg = '用户白名单'
                if res:
                    friends = {i.id: i.nickname for i in await self.app.getFriendList()}
                    for qq in res:
                        qq = int(qq[0])
                        if qq in friends.keys():
                            msg += f'\n{friends[qq]}: {qq}'
                        else:
                            msg += f'\n未知用户昵称: {qq}'
                else:
                    msg = '无激活用户'
                return MessageChain.create([Plain(msg)])
        elif subcommand.__contains__('blacklist'):
            if subcommand['blacklist'].__contains__('add'):
                target = other_args['qq'].target if isinstance(other_args['qq'], At) else other_args['qq']
                if Permission.compare(self.member if hasattr(self, 'group') else self.friend, target):
                    await BotUser(target).grant_level(0)
                    BANNED_USER.append(target)
                    return MessageChain.create([Plain('禁用成功!')])
                return self.not_admin()
            elif subcommand['blacklist'].__contains__('delete'):
                target = other_args['qq'].target if isinstance(other_args['qq'], At) else other_args['qq']
                if Permission.compare(self.member if hasattr(self, 'group') else self.friend, target):
                    await BotUser(target).grant_level(1)
                    if target in BANNED_USER:
                        BANNED_USER.remove(target)
                    return MessageChain.create([Plain('解除禁用成功!')])
                return self.not_admin()
            elif subcommand['blacklist'].__contains__('list'):
                with MysqlDao() as db:
                    res = db.query("SELECT uid FROM user WHERE level=0")
                return MessageChain.create([Plain('\r\n'.join([f'{qq[0]}' for qq in res]) if res else '无黑名单用户')])
        elif subcommand.__contains__('group'):
            if subcommand['group'].__contains__('add'):
                BotGroup(other_args['group'], active=1)
                ACTIVE_GROUP.update({other_args['group']: '*'})
                return MessageChain.create([Plain('激活成功!')])
            elif subcommand['group'].__contains__('delete'):
                await BotGroup(other_args['group'], active=0).group_deactivate()
                if other_args['group'] in ACTIVE_GROUP:
                    ACTIVE_GROUP.pop(other_args['group'])
                return MessageChain.create([Plain('禁用成功!')])
            elif subcommand['group'].__contains__('list'):
                with MysqlDao() as db:
                    res = db.query("SELECT uid FROM `group` WHERE active=1")
                msg = '群组白名单'
                if res:
                    groups = {i.id: {'name': i.name, 'perm': i.accountPerm.value} for i in await self.app.getGroupList()}
                    for group_id in res:
                        group_id = int(group_id[0])
                        if group_id in groups.keys():
                            msg += f"\n{groups[group_id]['name']}: {group_id} - {GROUP_PERM[groups[group_id]['perm']]}"
                        else:
                            msg += f"\n未知群: {group_id} - 未加入该群"
                else:
                    msg = '无白名单群组'
                return MessageChain.create([Plain(msg)])
        return self.args_error()

    @classmethod
    async def grant_permission_process(cls, user_id: int, new_level: int):
        """修改用户权限"""
        await BotUser(user_id).grant_level(new_level)
        return MessageChain.create([Plain(f'修改成功！\r\n{user_id} level: {new_level}')])


class DB(InitDB):

    async def process(self):
        with MysqlDao() as _db:
            _db.update(
                "create table if not exists user( \
                    id int auto_increment comment 'ID' primary key, \
                    uid char(12) null comment 'QQ', \
                    permission varchar(512) default '*' not null comment '许可', \
                    active int not null comment '状态', \
                    level int default 1 not null comment '权限', \
                    points int default 0 null comment '货币', \
                    signin_points int default 0 null comment '签到货币', \
                    english_answer int default 0 null comment '英语答题榜', \
                    last_login date comment '最后登陆')"
            )
            _db.update(
                "create table if not exists `group`( \
                    uid char(12) null comment '群号', \
                    permission varchar(512) not null comment '许可', \
                    active int not null comment '状态')"
            )
