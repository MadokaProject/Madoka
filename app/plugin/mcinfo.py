import asyncio
import json
import socket
import struct
import time

import jsonpath
from graia.application import MessageChain
from graia.application.message.elements.internal import Plain

from app.plugin.base import Plugin
from app.util.dao import MysqlDao
from app.util.decorator import permission_required


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
            name = jsonpath.jsonpath(response, '$..sample[..name]')
            if name:
                msg += "\r\n玩家: "
                for index in range(len(name)):
                    if index != 0:
                        msg += ', '
                    msg += name[index]
            return msg
        return response


class McStatus(Plugin):
    entry = ['.mc', '.mcinfo', '.info']
    brief_help = '\r\n▶MC状态：mc'
    full_help = \
        '.mc/.info/.mcinfo [ip] [port] [timeout]\r\n' \
        'ip: MC服务器域名或IP\r\n' \
        'port: MC服务器端口号\r\n' \
        'timeout: 设置超时时间'

    @permission_required(level='ADMIN')
    async def set_default_mc(self, ip='127.0.0.1', port=25565):
        default_ip, default_port = ip, port
        with MysqlDao() as db:
            res = db.update(
                'UPDATE mc_server SET `default`=0 WHERE `default`=1'
            )
            res = db.query(
                'SELECT COUNT(*) FROM mc_server WHERE ip=%s and port=%s',
                [default_ip, default_port]
            )
            if res[0][0]:
                res = db.update(
                    'UPDATE mc_server SET `default`=1 WHERE ip=%s and port=%s',
                    [default_ip, default_port]
                )
            else:
                res = db.update(
                    'INSERT INTO mc_server (ip, port, `default`, listen, delay) VALUES (%s, %s, 1, 0, 60)',
                    [default_ip, default_port]
                )
        self.resp = MessageChain.create([Plain('设置成功！')])

    async def process(self):
        try:
            with MysqlDao() as db:
                res = db.query('SELECT ip,port FROM mc_server WHERE `default`=1')
            default = [res[0][0], res[0][1]]
            if self.msg:
                if self.msg[0].startswith('set'):
                    await self.set_default_mc(*self.msg[1:])
                    return
                elif self.msg[0].startswith('ld'):
                    self.resp = MessageChain.create([
                        Plain(f'默认服务器: {default[0]}:{default[1]}\r\n')
                    ])
                    return
                else:
                    default = self.msg
            self.resp = MessageChain.create([Plain(
                StatusPing(*default).get_status(str_format=True))
            ])
        except EnvironmentError as e:
            print(e)
            self.resp = MessageChain.create([Plain(
                '由于目标计算机积极拒绝，无法连接。服务器可能已关闭。'
            )])
        except ValueError as e:
            print(e)
            self.arg_type_error()
        except Exception as e:
            print(e)
            self.unkown_error()


if __name__ == '__main__':
    a = McStatus(MessageChain.create([Plain('.mc')]))
    asyncio.run(a.get_resp())
    print(a.resp)
