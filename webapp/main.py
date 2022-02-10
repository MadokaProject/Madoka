from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from logging.config import dictConfig

from app.core.config import Config
from webapp.api.rest.health import Health

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s | %(levelname)-8s | %(module)s - %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
app = Flask(__name__)
app.config.update(RESTFUL_JSON=dict(ensure_ascii=False))
CORS(app, resources=r'/*')
api = Api(app)

api.add_resource(Health, '/api/rest/health')  # 机器人健康检查


def WebServer():
    config = Config()
    app.run(host=config.WEBSERVER_HOST, port=config.WEBSERVER_PORT, debug=config.WEBSERVER_DEBUG)
