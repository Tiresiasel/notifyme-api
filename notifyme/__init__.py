from flask import Flask
# from flask_cache import Cache
from flask_restful import Api
from flask_redis import FlaskRedis
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from notifyme import config



app = Flask(__name__)
app.config.from_object(config)

api = Api(app)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)

redis_client = FlaskRedis()
redis_client.init_app(app)


# cache = Cache()
# cache.init_app(app)
