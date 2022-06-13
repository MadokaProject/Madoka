import pickle
import time
from pathlib import Path

import jsonpath
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain

from app.plugin.basic.mcinfo import StatusPing


class McServer:
    status = False
    players = set()
    description = ''

    def __init__(self, default_ip='127.0.0.1', default_port=25565):
        self.ip = default_ip
        self.port = default_port
        self.update(init=True)
        self.time = time.time()

    def update(self, init=False):
        players = self.players.copy()
        description = self.description
        try:
            response = StatusPing(self.ip, self.port).get_status()
            status = True
            names = jsonpath.jsonpath(response, '$..sample[..name]')
            description = jsonpath.jsonpath(response, '$..description')[0]
            if jsonpath.jsonpath(description, '$..text'):
                description = jsonpath.jsonpath(description, '$..text')[-1]
            if names:
                for index in range(len(names)):
                    players.update({names[index]})
            else:
                players.clear()
        except (EnvironmentError, Exception):
            status = False
            players.clear()

        if init:
            self.status = status
            self.players = players
            self.description = description
        else:
            resp = MessageChain.create([
                Plain(f'地址：{self.ip}:{self.port}\r\n'),
                Plain(f'描述：{description}\r\n'),
                Plain(f'信息：\r\n')
            ])
            resp_content = MessageChain.create([])
            if status and (status != self.status):
                resp_content.extend(MessageChain.create([
                    Plain('服务器已开启！\r\n')
                ]))
            for player in self.players - players:
                resp_content.extend(MessageChain.create([
                    Plain(f'{player}退出了服务器！\r\n')
                ]))
            for player in players - self.players:
                resp_content.extend(MessageChain.create([
                    Plain(f'{player}加入了服务器！\r\n')
                ]))
            if (not status) and (status != self.status):
                resp_content.extend(MessageChain.create([
                    Plain('服务器已关闭！\r\n')
                ]))
            self.status = status
            self.players = players
            self.description = description
            self.time = time.time()
            if resp_content.__root__:
                resp.extend(resp_content)
                return resp
            return None


async def mc_listener(app, path: Path, ips, qq, delay_sec):
    file = path.joinpath(f'{ips[0]}_{str(ips[1])}.dat')
    if file.exists():
        with open(file, 'rb') as f:
            obj = pickle.load(f)
    else:
        obj = McServer(*ips)
    if time.time() - obj.time > int(1.5 * delay_sec):
        obj = McServer(*ips)
    resp = obj.update()
    with open(file, 'wb') as f:
        pickle.dump(obj, f)
    if not resp:
        return
    for target in qq:
        if target[0] == 'f':
            target = await app.getFriend(int(target[1:]))
            if not target:
                continue
            await app.sendFriendMessage(target, resp)
        elif target[0] == 'g':
            target = await app.getGroup(int(target[1:]))
            if not target:
                continue
            await app.sendGroupMessage(target, resp)
