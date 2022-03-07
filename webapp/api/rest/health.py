import threading

from flask_restful import Resource

from webapp.util.tools import GET_RET_JSON


class Health(Resource):
    @classmethod
    def get(cls):
        threads = threading.enumerate()
        for thread in threads:
            if not thread.is_alive():
                return GET_RET_JSON(502, 'death'), 502
        return GET_RET_JSON(200, 'success'), 200
