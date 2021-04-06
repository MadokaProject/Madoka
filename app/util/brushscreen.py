from app.util.dao import MysqlDao


def brushscreen(group_id, member_id):
    with MysqlDao() as db:
        res = db.query('SELECT * FROM msg where uid=%s and qid=%s', [group_id, member_id])[-3:]
        if len(res) > 2:
            time = (res[2][3] - res[0][3]).seconds
            if time < 5:  # 刷屏禁言
                return 1
            elif res[0][4] == res[1][4] == res[2][4] \
                    and res[0][4].strip() != '' and time < 30:  # 30秒内重复消息禁言
                return 2
            else:
                return 0


if __name__ == '__main__':
    print(brushscreen(1042210644, 1332925715))
