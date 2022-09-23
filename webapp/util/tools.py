def GET_RET_JSON(code_id, msg=None, data=None):
    ret = {'code': code_id, 'msg': 'null'}
    if msg:
        ret['msg'] = msg
    if data or data == {}:
        ret['data'] = data
    return ret
