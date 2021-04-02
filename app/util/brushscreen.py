import datetime

from app.util import mysql


def brushscreen(record_table, qq):
    Message_history = mysql.record_find(record_table, qq)
    time1 = datetime.datetime.strptime(Message_history[0][2], '%Y-%m-%d %H:%M:%S')
    time2 = datetime.datetime.strptime(Message_history[2][2], '%Y-%m-%d %H:%M:%S')
    if (time2 - time1).seconds < 5:  # 刷屏禁言
        return 1
    elif Message_history[0][3] == Message_history[1][3] == Message_history[2][3] \
            and Message_history[0][3].strip() != '':  # 重复消息禁言
        return 2
    else:
        return 0
