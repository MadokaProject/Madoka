import getopt

from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import At, Plain
from loguru import logger

from app.core.settings import ADMIN_USER


async def power(app, argv):
    upgrade = None
    shutdown = False
    group = False
    reboot = False
    target = await app.get_friend(ADMIN_USER[0])
    try:
        opts, args = getopt.getopt(
            argv[1:],
            "-r-k-u:-g:-t:",
            ["reboot", "kill", "upgrade=", "group=", "target="],
        )
    except getopt.GetoptError:
        await app.send_friend_message(target, MessageChain([Plain("脚本参数错误")]))
        return
    for opt, arg in opts:
        if opt == "-h":
            await app.send_friend_message(
                target,
                MessageChain(
                    [
                        Plain("\t-r\t--reboot\t重启成功\r\n"),  # 有此参数代表重启成功 [可选]
                        Plain("\t-k\t--kill\t关闭失败\r\n"),  # 有此参数代表关闭失败 [可选]
                        Plain("\t-u\t--upgrade\t升级状态\r\n"),  # 此参数代表升级成功(true)/失败(false) [可选]
                        Plain("\t\t例如：-u true, --upgrade=true\r\n"),
                        Plain("\t-g\t--group\t来自群组\r\n"),  # 此参数代表来自群组 [可选]
                        Plain("\t\t例如：-g 123, --group=123\r\n"),
                        Plain("\t-t\t--target\t执行者\r\n"),  # 此参数代表命令执行者 <建议必选>
                        Plain("\t\t例如：-e 123, --e=123\r\n"),
                    ]
                ),
            )
            return
        elif opt in ("-r", "--reboot"):
            reboot = True
        elif opt in ("-k", "--kill"):
            shutdown = True
        elif opt in ("-u", "--upgrade"):
            upgrade = True if arg == "true" else False
        elif opt in ("-g", "--group"):
            group = await app.get_group(int(arg))
        elif opt in ("-t", "--target"):
            target = await app.get_friend(int(arg))
    if group:
        target = await app.get_member(group, target.id)
    if shutdown:
        if group:
            await app.send_group_message(group, MessageChain([At(target.id), Plain(" 进程未正常结束！")]))
        else:
            await app.send_friend_message(target, MessageChain([Plain("进程未正常结束！")]))
        logger.warning("进程未正常结束！")
        return
    if reboot:
        if group:
            await app.send_group_message(group, MessageChain([At(target.id), Plain(" 重启成功！")]))
        else:
            await app.send_friend_message(target, MessageChain([Plain("重启成功！")]))
        logger.success("重启成功！")
        return
    if upgrade is not None:
        if upgrade:
            if group:
                await app.send_group_message(group, MessageChain([At(target.id), Plain(" 升级成功！")]))
            else:
                await app.send_friend_message(target, MessageChain([Plain("升级成功！")]))
            logger.success("升级成功！")
        else:
            if group:
                await app.send_group_message(group, MessageChain([At(target.id), Plain(" 升级失败！")]))
            else:
                await app.send_friend_message(target, MessageChain([Plain("升级失败！")]))
            logger.error("升级失败！")
