import mysql
import datetime


def brushscreen(record_table, qq, message, now_time):
    Message_history = mysql.record_find(record_table, qq)
    time1 = datetime.datetime.strptime(Message_history[0][2], '%Y-%m-%d %H:%M:%S')
    time2 = datetime.datetime.strptime(Message_history[2][2], '%Y-%m-%d %H:%M:%S')
    if (time2 - time1).seconds < 5:
        return 1
    else:
        return 0
