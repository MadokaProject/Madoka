import subprocess
import sys

from graia.application import MessageChain
from graia.application.message.elements.internal import At, Plain

from app.plugin.base import Plugin
from app.util.decorator import permission_required
from app.util.tools import isstartswith, restart


class Admin(Plugin):
    entry = ['.power', '.电源', '.p']
    brief_help = '\r\n▶电源：p'
    full_help = \
        '.电源/.p\t仅限管理员使用！\r\n' \
        '.电源/.p k\t关闭机器人\r\n' \
        '.电源/.p r\t重启机器人\r\n' \
        '.电源/.p u [timeout]\t升级机器人(默认超时时间为10秒)\r\n'
    hidden = True

    @permission_required(level='ADMIN')
    async def process(self):
        if not self.msg:
            self.print_help()
            return
        try:
            if isstartswith(self.msg[0], ['k', 'u', 'r']):
                shell = ''
                if hasattr(self, 'group'):
                    shell = [f'-g {self.group.id}', f'-t {self.member.id}']
                elif hasattr(self, 'friend'):
                    shell = f'-t {self.friend.id}'
                if isstartswith(self.msg[0], 'u'):
                    timeout = 10
                    if len(self.msg) == 2 and self.msg[1].isdigit():
                        timeout = int(self.msg[1])
                    try:
                        ret = subprocess.call('git pull', timeout=timeout, shell=True)
                        if ret == 0:
                            restart('-u', 'true', *shell)
                        else:
                            restart('-u', 'false', *shell)
                    except subprocess.TimeoutExpired:
                        if hasattr(self, 'group'):
                            self.resp = MessageChain.create([
                                At(self.member.id),
                                Plain(" 升级超时！")
                            ])
                        else:
                            self.resp = MessageChain.create([
                                Plain("升级超时！")
                            ])
                elif isstartswith(self.msg[0], 'r'):
                    restart('-r', *shell)
                sys.exit()
            else:
                self.args_error()
                return
        except Exception as e:
            print(e)
            self.unkown_error()
