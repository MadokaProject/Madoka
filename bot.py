import asyncio
import mysql
import requests
import datetime
import brushscreen
from config import *
from graia.broadcast import Broadcast
from graia.application import GraiaMiraiApplication, Session
from graia.application.message.chain import MessageChain
from graia.application.message.elements.internal import Plain, Image, At
from graia.application.friend import Friend
from graia.application.group import Group, Member

loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host=host,  # 填入 httpapi 服务运行的地址
        authKey=authKey,  # 填入 authKey
        account=qq,  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)


@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, friend: Friend):
    await app.sendFriendMessage(friend, MessageChain.create([
        Plain("您好，我的功能还在开发中~~~"), Image.fromNetworkAddress("https://tenapi.cn/acg/")
    ]))


@bcc.receiver("GroupMessage")
async def group_message_listener(message: MessageChain, group: Group, member: Member, app: GraiaMiraiApplication):
    if member.id != admin_qq:
        table_record_name = str(group.id) + 'record'  # 聊天记录数据库名
        curr_time = datetime.datetime.now()  # 获取当前时间
        time_str = datetime.datetime.strftime(curr_time, '%Y-%m-%d %H:%M:%S')  # 转换为str
        content_record = ''
        try:  # 获取文字类型的聊天记录
            content_record = message.get(Plain)[0].dict()['text']
        except:  # 获取图片类型的聊天记录
            content_record = message.get(Image)[0].dict()['url']
        # 存入数据库
        if mysql.find_table(table_record_name):  # 若数据表已存在
            mysql.insert_record(table_record_name, str(member.id), time_str, content_record)
        else:  # 若数据表不存在
            mysql.create_record(table_record_name)  # 先创建数据表
            mysql.insert_record(table_record_name, str(member.id), time_str, content_record)

    # 检测是否刷屏
    if member.id != admin_qq:
        target_brushscreen = brushscreen.brushscreen(table_record_name, str(member.id), content_record, time_str)
        if target_brushscreen == 1:
            await app.mute(group, member, 5 * 60)
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id), Plain(" 请勿刷屏")
            ]))
        elif target_brushscreen == 2:
            await app.mute(group, member, 2 * 60)
            await app.sendGroupMessage(group, MessageChain.create([
                At(member.id), Plain(" 请勿发送重复消息")
            ]))

    # print(message.has(At))
    target = message.get(At)
    # 判断是否有At
    if target:
        target = target[0]
        if target.dict()['target'] == 2817736127:
            if member.id == admin_qq:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("管理员您好")
                ]))
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("爪巴")
                ]))
            return
    # for i in ReplyKey:
    #     if str(message.get(Plain)[0].dict()['text']).strip() == i[0]:
    #         if i[1] == 'text':
    #             await app.sendGroupMessage(group, MessageChain.create([
    #                 Plain(i[2])
    #             ]))
    #             return
    #         elif i[1] == 'image':
    #             await app.sendGroupMessage(group, MessageChain.create([
    #                 Image.fromNetworkAddress(i[2])
    #             ]))
    #             return

    table_name_home = str(group.id) + 'group'
    Custom_message = message.get(Plain)
    Custom_message = Custom_message[0].dict()['text'].split(' ')
    if str(message.get(Plain)[0].dict()['text']).strip() == '.help':  # 内置指令放这
        if mysql.find_table(table_name_home):  # 若数据表存在
            menu_list = mysql.find(table_name_home)
            menu = '=====帮助菜单=====\n'  # 初始化帮助菜单
            for i in menu_list:
                menu = menu + i[1] + '\n'
            menu += '================='
            print(menu)
            await app.sendGroupMessage(group, MessageChain.create([
                Plain(menu)
            ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("本群暂未添加指令")
            ]))
        return
    elif str(message.get(Plain)[0].dict()['text']).strip() == '.wyy' or str(
            message.get(Plain)[0].dict()['text']).strip() == '.网易云':
        req = requests.get('https://api.66mz8.com/api/music.163.php?format=json')
        ans = req.json()
        await app.sendGroupMessage(group, MessageChain.create([
            Plain('歌曲：%s\r\n' % ans['name']),
            Plain('昵称：%s\r\n' % ans['nickname']),
            Plain('评论：%s' % ans['comments'])
        ]))
        return
    elif Custom_message[0] == '.ban':   # 禁言
        if member.id == admin_qq:
            target = message.get(At)
            if target:  # 如若有at人
                target = target[0].dict()['target']
                print(target)
                print(int(Custom_message[1]) * 60)
                await app.mute(group, target, int(Custom_message[1]) * 60)
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("缺少参数")
                ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("你不是管理员哦，你无权操作此命令！")
            ]))
    elif str(message.get(Plain)[0].dict()['text']).strip() == '.unban': # 取消禁言
        if member.id == admin_qq:
            target = message.get(At)
            if target:  # 如若有at人
                target = target[0].dict()['target']
                await app.unmute(group, target)
            else:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("缺少参数")
                ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("你不是管理员哦，你无权操作此命令！")
            ]))
        return
    if Custom_message[0] == '.message' and Custom_message[1] == 'add':
        if member.id == admin_qq:
            try:
                if Custom_message[3] == 'text' or Custom_message[3] == 'image':
                    target = 0
                    if mysql.find_table(table_name_home):  # 若数据表已存在
                        target = mysql.insert(table_name_home, Custom_message[2], Custom_message[3], Custom_message[4])
                    else:  # 若数据表不存在
                        target_create = mysql.create(table_name_home)  # 先创建数据表
                        if target_create == 1:
                            target = mysql.insert(table_name_home, Custom_message[2], Custom_message[3],
                                                  Custom_message[4])
                        elif target_create == 0:
                            target = 0
                    if target == 1:
                        await app.sendGroupMessage(group, MessageChain.create([
                            Plain("添加成功")
                        ]))
                    elif target == -1:
                        await app.sendGroupMessage(group, MessageChain.create([
                            Plain("添加的指令已存在")
                        ]))
                    else:
                        await app.sendGroupMessage(group, MessageChain.create([
                            Plain("添加失败")
                        ]))
                else:
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain("指令参数错误，你必须使用text、image")
                    ]))
            except:
                await app.sendGroupMessage(group, MessageChain.create([
                    Plain("指令参数错误，你必须使用text、image")
                ]))
        else:
            await app.sendGroupMessage(group, MessageChain.create([
                Plain("抱歉，您不是管理员，您不能使用该指令")
            ]))
        return
    print(mysql.find_table(table_name_home))
    if mysql.find_table(table_name_home):  # 若数据表存在
        Reply = mysql.find(table_name_home)  # 返回表内容
        print(Reply)
        for i in Reply:
            if str(message.get(Plain)[0].dict()['text']).strip() == i[1]:  # 指令对比
                if i[2] == 'text':
                    await app.sendGroupMessage(group, MessageChain.create([
                        Plain(i[3])
                    ]))
                    return
                elif i[2] == 'image':
                    await app.sendGroupMessage(group, MessageChain.create([
                        Image.fromNetworkAddress(i[3])
                    ]))
                    return


app.launch_blocking()
