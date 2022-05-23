from flask import Flask
# from flask_cache import Cache
from flask_restful import Api
from flask_redis import FlaskRedis
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from . import config
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.config.from_object(config)

api = Api(app)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

redis_client = FlaskRedis()
redis_client.init_app(app)

CORS(app, supports_credentials=True, origins='*',
     headers=['Content-Type', 'Authorization'],
     expose_headers='Authorization',
     method=["post","get","options"]	)
