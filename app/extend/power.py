import getopt

from graia.application import MessageChain
from graia.application.message.elements.internal import Plain, At

from app.core.settings import *


async def power(app, argv):
    upgrade = None
    shutdown = False
    group = False
    reboot = False
    target = await app.getFriend(ADMIN_USER[0])
    try:
        opts, args = getopt.getopt(argv[1:], '-r-k-u:-g:-t:', ['reboot', 'kill', 'upgrade=', 'group=', 'target='])
    except getopt.GetoptError:
        await app.sendFriendMessage(target, MessageChain.create([Plain("脚本参数错误")]))
        return
    for opt, arg in opts:
        if opt == '-h':
            await app.sendFriendMessage(target, MessageChain.create([
                Plain('\t-r\t--reboot\t重启成功\r\n'),  # 有此参数代表重启成功 [可选]
                Plain('\t-k\t--kill\t关闭失败\r\n'),    # 有此参数代表关闭失败 [可选]
                Plain('\t-u\t--upgrade\t升级状态\r\n'),  # 此参数代表升级成功(true)/失败(false) [可选]
                Plain('\t\t例如：-u true, --upgrade=true\r\n'),
                Plain('\t-g\t--group\t来自群组\r\n'),  # 此参数代表来自群组 [可选]
                Plain('\t\t例如：-g 123, --group=123\r\n'),
                Plain('\t-e\t--target\t执行者\r\n'),  # 此参数代表命令执行者 <建议必选>
                Plain('\t\t例如：-e 123, --e=123\r\n'),
            ]))
            return
        elif opt in ('-r', '--reboot'):
            reboot = True
        elif opt in ('-k', '--kill'):
            shutdown = True
        elif opt in ('-u', '--upgrade'):
            upgrade = True if arg == 'true' else False
        elif opt in ('-g', '--group'):
            group = await app.getGroup(int(arg))
        elif opt in ('-t', '--target'):
            target = await app.getFriend(int(arg))
    if group:
        target = await app.getMember(group.id, target.id)
    if shutdown:
        if group:
            await app.sendGroupMessage(group, MessageChain.create([
                At(target.id),
                Plain(' 进程未正常结束！')
            ]))
        else:
            await app.sendFriendMessage(target, MessageChain.create([
                Plain('进程未正常结束！')
            ]))
        return
    if reboot:
        if group:
            await app.sendGroupMessage(group, MessageChain.create([
                At(target.id),
                Plain(' 重启成功！')
            ]))
        else:
            await app.sendFriendMessage(target, MessageChain.create([
                Plain('重启成功！')
            ]))
        return
    if upgrade is not None:
        if upgrade:
            if group:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(target.id),
                    Plain(' 升级成功！')
                ]))
            else:
                await app.sendFriendMessage(target, MessageChain.create([
                    Plain('升级成功！')
                ]))
        else:
            if group:
                await app.sendGroupMessage(group, MessageChain.create([
                    At(target.id),
                    Plain(' 升级失败！')
                ]))
            else:
                await app.sendFriendMessage(target, MessageChain.create([
                    Plain('升级失败！')
                ]))
