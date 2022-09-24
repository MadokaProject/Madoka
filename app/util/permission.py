from typing import Union

from graia.ariadne.model import Friend, Group

from app.core.settings import ACTIVE_GROUP, ACTIVE_USER, ADMIN_USER


def check_permit(qid: Union[Friend, Group], cmd: str):
    if isinstance(qid, Group):
        qid: int = qid.id
        if qid in ACTIVE_GROUP.keys():
            if f"-{cmd}" in ACTIVE_GROUP[qid]:
                return False
            elif "*" in ACTIVE_GROUP[qid] or cmd in ACTIVE_GROUP[qid]:
                return True
    else:
        qid: int = qid.id
        if qid in ADMIN_USER:
            return True
        elif qid in ACTIVE_USER.keys():
            if f"-{cmd}" in ACTIVE_USER[qid]:
                return False
            elif "*" in ACTIVE_USER[qid] or cmd in ACTIVE_USER[qid]:
                return True

    return False
