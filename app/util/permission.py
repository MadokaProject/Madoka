from typing import Union

from graia.ariadne.model import Friend, Member

from app.core.settings import *


def check_permit(qid: Union[Friend, Member], cmd: str):
    qid: int = qid.id
    if isinstance(qid, Member):
        if qid in ACTIVE_GROUP.keys():
            if '-' + cmd in ACTIVE_GROUP[qid]:
                return False
            elif '*' in ACTIVE_GROUP[qid]:
                return True
            elif cmd in ACTIVE_GROUP[qid]:
                return True
        return False
    else:
        if qid in ADMIN_USER:
            return True
        elif qid in ACTIVE_USER.keys():
            if '-' + cmd in ACTIVE_USER[qid]:
                return False
            elif '*' in ACTIVE_USER[qid]:
                return True
            elif cmd in ACTIVE_USER[qid]:
                return True
        return False
