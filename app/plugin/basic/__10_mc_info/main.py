import json
import pickle
import socket
import struct
import time
from typing import Union

import jsonpath
from arclet.alconna import Alconna, Subcommand, Option, Args, Arpamar
from graia.ariadne import Ariadne
from graia.ariadne.model import Friend, Member, Group
from graia.scheduler import timers, GraiaScheduler
from loguru import logger
from peewee import OperationalError

from app.core.app import AppCore
from app.core.commander import CommandDelegateManager
from app.util.control import Permission
from app.util.phrases import *
from app.util.tools import app_path
from .database.database import McServer as DBMcServer

core: AppCore = AppCore()
app: Ariadne = core.get_app()
sche: GraiaScheduler = core.get_scheduler()
manager: CommandDelegateManager = CommandDelegateManager()
path = app_path().joinpath('tmp/mcserver')
path.mkdir(parents=True, exist_ok=True)

try:
    LISTEN_MC_SERVER = {
        (_.host, int(_.port)): {
            'report': [i for i in str(_.report).split(',') if i.strip()],
            'delay': _.delay
        } for _ in DBMcServer.select().where(DBMcServer.listen == 1)
    }
    """MC服务器自动监听列表"""
except OperationalError:
    LISTEN_MC_SERVER = {}
    logger.warning('数据表读取异常，无法自动监听MC服务器')


@manager.register(
    entry='mc',
    brief_help='MC状态',
    alc=Alconna(
        headers=manager.headers,
        command='mc',
        options=[
            Subcommand(
                'default', help_text='设置默认MC服务器(仅主人可用)',
                args=Args['host;H', str, '127.0.0.1']['port;H', int, 25565]
            ),
            Subcommand(
                'set', help_text='设置监听服务器(仅主人可用)',
                args=Args['host;H', str, '127.0.0.1']['port;H', int, 25565]['delay;H', int, 60], options=[
                    Option('on', help_text='开启监听(默认)'),
                    Option('off', help_text='关闭监听')
                ]
            ),
            Subcommand(
                'listen', help_text='配置监听服务器',
                args=Args['host;H', str, '127.0.0.1']['port;H', int, 25565],
                options=[
                    Option('on', help_text='开启监听(默认)'),
                    Option('off', help_text='关闭监听')
                ]
            ),
            Option('--timeout|-t', help_text='超时时间', args=Args['timeout', int]),
            Option('--view|-v', help_text='查看')
        ],
        main_args=Args['host;O|H', str]['port;O|H', int],
        help_text='检测MC服务器信息'
    )
)
async def process(cmd: Arpamar, target: Union[Friend, Member], sender: Union[Friend, Group]):
    try:
        if all([cmd.find('set'), Permission.manual(target, Permission.MASTER)]):
            if cmd.find('view'):
                msg = '正在监听的服务器:\n' + ''.join(f'{i[0]}: {i[1]}\n' for i in LISTEN_MC_SERVER.keys())
                msg += '已设置的监听服务器:\n' + \
                       '\n'.join(f'{_.host}: {_.port}' for _ in DBMcServer.select().where(DBMcServer.listen == 1))
                return MessageChain(msg)
            status = 0 if 'off' in cmd['set']['options'] else 1
            DBMcServer.replace(
                host=cmd.query('host'),
                port=cmd.query('port'),
                listen=status,
                delay=cmd.query('delay')
            ).execute()
            return MessageChain('设置成功, 重启后生效!')
        elif cmd.find('default'):
            if cmd.find('view'):
                if default_server := DBMcServer.get_or_none(default=1):
                    return MessageChain(f'默认服务器：{default_server.host}:{default_server.port}')
                return MessageChain('未设置默认服务器')
            return await set_default_mc(target, cmd.query('host'), cmd.query('port'))
        elif cmd.find('listen'):
            if isinstance(sender, Friend):
                target = f'f{sender.id}'
                msg = '您正在监听的服务器:\n'
            elif isinstance(sender, Group) and not Permission.manual(target, Permission.GROUP_ADMIN) \
                    and not cmd.find('view'):
                return not_admin()
            else:
                target = f'g{sender.id}'
                msg = '本群正在监听的服务器:\n'
            if cmd.find('view'):
                for k, v in LISTEN_MC_SERVER.items():
                    if target in v['report']:
                        msg += f'{k[0]}: {k[1]}\n'
                return MessageChain(msg)
            if not (
                res := DBMcServer.get_or_none(
                    host=cmd.query('host'), port=cmd.query('port')
                )
            ):
                return MessageChain('未找到该服务器，请联系管理员添加!')
            res.report = res.report or ''
            report = (
                ','.join(filter(lambda x: x != target, res.report.split(',')))
                if 'off' in cmd['listen']['options']
                else ','.join({target, *res.report.split(',')})
            )

            DBMcServer.update(report=report).where(
                (DBMcServer.host == cmd.query('host')) & (DBMcServer.port == cmd.query('port'))
            ).execute()
            logger.info(type(report))
            LISTEN_MC_SERVER[(cmd.query('host'), cmd.query('port'))]['report'] = [i for i in report.split(',') if i]
            return MessageChain('设置成功!')
        else:
            if res := DBMcServer.get_or_none(default=1):
                default = (cmd.query('host') or res.host, cmd.query('port') or res.port, cmd.query('timeout'))
            else:
                default = (cmd.query('host') or '127.0.0.1', cmd.query('port') or 25565, cmd.query('timeout') or 10)
            return MessageChain(StatusPing(*default).get_status(str_format=True))
    except EnvironmentError as e:
        logger.warning(e)
        return MessageChain([Plain('由于目标计算机积极拒绝，无法连接。服务器可能已关闭。')])
    except ValueError:
        return arg_type_error()
    except Exception as e:
        logger.exception(e)
        return unknown_error()


@Permission.require(level=Permission.MASTER)
async def set_default_mc(_: Union[Friend, Member], host='127.0.0.1', port=25565):
    DBMcServer.update(default=0).where(DBMcServer.default == 1).execute()
    if DBMcServer.get_or_none(DBMcServer.host == host and DBMcServer.port == port):
        DBMcServer.update(default=1).where(DBMcServer.host == host and DBMcServer.port == port).execute()
    else:
        DBMcServer.create(host=host, port=port, default=1)
    return MessageChain([Plain('设置成功!')])


class StatusPing:
    """ Get the ping status for the Minecraft server """

    def __init__(self, host='127.0.0.1', port=25565, timeout=10):
        """ Init the hostname and the port """
        self._host = host
        self._port = int(port)
        self._timeout = timeout

    @staticmethod
    def _unpack_varint(sock):
        """ Unpack the varint """
        data = 0
        for i in range(5):
            ordinal = sock.recv(1)

            if len(ordinal) == 0:
                break

            byte = ord(ordinal)
            data |= (byte & 0x7F) << 7 * i

            if not byte & 0x80:
                break

        return data

    @staticmethod
    def _pack_varint(data):
        """ Pack the var int """
        ordinal = b''
        while True:
            byte = data & 0x7F
            data >>= 7
            ordinal += struct.pack('B', byte | (0x80 if data > 0 else 0))

            if data == 0:
                break

        return ordinal

    def _pack_data(self, data):
        """ Page the data """
        if type(data) is str:
            data = data.encode('utf8')
            return self._pack_varint(len(data)) + data
        elif type(data) is int:
            return struct.pack('H', data)
        elif type(data) is float:
            return struct.pack('Q', int(data))
        else:
            return data

    def _send_data(self, connection, *args):
        """ Send the data on the connection """
        data = b''

        for arg in args:
            data += self._pack_data(arg)

        connection.send(self._pack_varint(len(data)) + data)

    def _read_fully(self, connection, extra_varint=False):
        """ Read the connection and return the bytes """
        packet_length = self._unpack_varint(connection)
        packet_id = self._unpack_varint(connection)
        byte = b''

        if extra_varint:
            # Packet contained netty header offset for this
            if packet_id > packet_length:
                self._unpack_varint(connection)

            extra_length = self._unpack_varint(connection)

            while len(byte) < extra_length:
                byte += connection.recv(extra_length)

        else:
            byte = connection.recv(packet_length)

        return byte

    def get_status(self, str_format=False):
        """ Get the status response """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            connection.settimeout(self._timeout)
            connection.connect((self._host, self._port))

            # Send handshake + status request
            self._send_data(connection, b'\x00\x00', self._host, self._port, b'\x01')
            self._send_data(connection, b'\x00')

            # Read response, offset for string length
            data = self._read_fully(connection, extra_varint=True)

            # Send and read unix time
            self._send_data(connection, b'\x01', time.time() * 1000)
            unix = self._read_fully(connection)

        # Load json and return
        response = json.loads(data.decode('utf8'))
        response['ping'] = int(time.time() * 1000) - struct.unpack('Q', unix)[0]

        if str_format:
            _version = jsonpath.jsonpath(response, '$..version[name]')[0]
            _description = jsonpath.jsonpath(response, '$..description')[0]
            if jsonpath.jsonpath(_description, '$..text'):
                _description = jsonpath.jsonpath(_description, '$..text')[-1]
            _ping = jsonpath.jsonpath(response, '$..ping')[0]
            _max = jsonpath.jsonpath(response, '$..online')[0]
            _online = jsonpath.jsonpath(response, '$..max')[0]
            msg = "版本: %s\r\n描述: %s\r\n延迟: %d ms\r\n在线: %d/%d" % (
                _version, _description, _ping, _max, _online)
            if name := jsonpath.jsonpath(response, '$..sample[..name]'):
                msg += "\r\n玩家: "
                for index in range(len(name)):
                    if index != 0:
                        msg += ', '
                    msg += name[index]
            return msg
        return response


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
            resp = MessageChain([
                Plain(f'地址：{self.ip}:{self.port}\r\n'),
                Plain(f'描述：{description}\r\n'),
                Plain(f'信息：\r\n')
            ])
            resp_content = MessageChain([])
            if status and (status != self.status):
                resp_content.extend(MessageChain([
                    Plain('服务器已开启！\r\n')
                ]))
            for player in self.players - players:
                resp_content.extend(MessageChain([
                    Plain(f'{player}退出了服务器！\r\n')
                ]))
            for player in players - self.players:
                resp_content.extend(MessageChain([
                    Plain(f'{player}加入了服务器！\r\n')
                ]))
            if (not status) and (status != self.status):
                resp_content.extend(MessageChain([
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


async def mc_listener(ips):
    file = path.joinpath(f'{ips[0]}_{str(ips[1])}.dat')
    if file.exists():
        with open(file, 'rb') as f:
            obj = pickle.load(f)
    else:
        obj = McServer(*ips)
    if time.time() - obj.time > int(1.5 * LISTEN_MC_SERVER[ips]['delay']):
        obj = McServer(*ips)
    resp = obj.update()
    with open(file, 'wb') as f:
        pickle.dump(obj, f)
    if not resp:
        return
    for target in LISTEN_MC_SERVER[ips]['report']:
        if target == '':
            continue
        if target[0] == 'f':
            target = await app.get_friend(int(target[1:]))
            if not target:
                continue
            await app.send_friend_message(target, resp)
        elif target[0] == 'g':
            target = await app.get_group(int(target[1:]))
            if not target:
                continue
            await app.send_group_message(target, resp)


for k, v in LISTEN_MC_SERVER.items():
    @sche.schedule(timers.every_custom_seconds(v['delay']))
    async def mc_listen_schedule():
        if config.ONLINE:
            await mc_listener(k)
