import random
from flask import jsonify, request
from modules import app, db, api, redis_client
from modules.models import NewsModel, NewsKeywordModel, UserModel, UserKeywordModel
from flask_restful import Resource, reqparse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from modules.error import *
from utils.auth import auth
from utils.email_template import CodeEmailContent
from utils.send_email import SendEmail
from flask_cors import cross_origin


def _check_if_email_exists(email: str) -> bool:
    news_ids = UserModel.query.filter_by(email=email).all()
    if news_ids:
        return True
    else:
        return False


class UserToken:
    """
    这个类负责token的获取与id的验证
    """

    def __init__(self):
        self.token = str(request.headers.get('Authorization')).split(' ')[-1]
        self.user_id = self._get_user_id_from_token()

    def _get_user_id_from_token(self):
        """解析令牌信息"""
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(self.token, return_header=True)
        # token过期
        except SignatureExpired:
            raise AuthFailed(msg='token is expired', error_code=1001)
        # 错误token异常
        except BadSignature:
            raise AuthFailed(msg='token is invalid', error_code=1002)
        return data[0]['uid']


class CORSResource(Resource):
    def options(self):
        return {'Allow': '*'}, 200, {'Access-Control-Allow-Origin': '*',
                                     'Access-Control-Allow-Methods': 'HEAD, OPTIONS, GET, POST, DELETE, PUT',
                                     'Access-Control-Allow-Headers': 'Content-Type, Content-Length, Authorization, Accept, X-Requested-With , yourHeaderField',
                                     }


class News(CORSResource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('keyword', type=str, required=True)
        self.parser.add_argument('limit', type=str)

    def get(self):
        # 获取特定keyword的新闻
        # 从news_keyword表中获取news的id
        data = self.parser.parse_args()
        keyword = data.get("keyword")
        limit = data.get("limit")

        news_ids = NewsKeywordModel.query.with_entities(NewsKeywordModel.news_id) \
            .filter_by(keyword=keyword)
        news_id = list(map(lambda x: x[0], news_ids))
        if limit:
            news_list_model = NewsModel.query.filter(NewsModel.id.in_(news_id)) \
                .order_by(NewsModel.publish_time).limit(limit).all()
        else:
            news_list_model = NewsModel.query.filter(
                NewsModel.id.in_(news_id)).all()
        news_list = []
        for news in news_list_model:
            news_list.append(news.to_json())
        return {"code": "200", "status": "OK", "data": news_list}


class UserEmailExist(CORSResource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True)

    def get(self):
        # 返回该邮箱是否存在
        data = self.parser.parse_args()
        email = data.get("email")
        status = _check_if_email_exists(email)
        if _check_if_email_exists(email):
            return {"code": 200, "status": "OK", "data": {"email_exist": status}}
        else:
            return {"code": 200, "status": "OK", "data": {"email_exist": status}}


class UserRegister(CORSResource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True)
        self.parser.add_argument("password_hash", type=str)
        self.parser.add_argument("username", type=str)

    def post(self):
        data = self.parser.parse_args()
        email = data.get("email")
        username = data.get("username")
        password_hash = data.get("password_hash")
        if _check_if_email_exists(email=email):  # 如果该邮件在数据库内存在
            return {"code": 406, "status": "Not Acceptable: user already exists"}
        else:
            user_to_add = UserModel(username=username, email=email, password_hash=password_hash)
            db.session.add(user_to_add)
            db.session.commit()
            return {"code": 201, "status": "Created"}


class UserLogin(CORSResource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True)
        self.parser.add_argument("password_hash", type=str, required=True)

    @staticmethod
    def _check_if_password_hash_equals(email: str, password_hash: str) -> bool:
        db_password_hash = UserModel.query.with_entities(UserModel.password_hash).filter_by(email=email).first()[0]
        if db_password_hash == password_hash:
            return True
        else:
            return False

    @staticmethod
    def _generate_auth_token(uid: int, expiration=60 * 60 * 24):
        # 通过flask提供的对象，传入过期时间和flask的SECRET_KEY
        """生成令牌"""
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'uid': uid}).decode('ascii')

    def get(self):
        data = self.parser.parse_args()
        email = data.get("email")
        password_hash = data.get("password_hash")
        if self._check_if_password_hash_equals(email=email, password_hash=password_hash):
            uid = UserModel.query.with_entities(UserModel.id).filter_by(email=email).first()[0]
            return {"code": 200, "status": "OK", "data": {"token": self._generate_auth_token(uid)}}
        else:
            return {"code": 401, "status": "Unauthorized"}


class UserSubscriptionKeyword(CORSResource, UserToken):
    def __init__(self):
        super().__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("keywords", type=str, required=True)  # 前端传入list的字符串，后端解析
        self.parser.add_argument("operation", type=str, required=True)

    @auth.login_required()
    def get(self):
        subscribed_keywords_list = UserKeywordModel.query.with_entities(UserKeywordModel.keyword) \
            .filter_by(user_id=self.user_id).all()
        keywords_list = []
        if subscribed_keywords_list:
            for keyword in subscribed_keywords_list:
                keywords_list.append(keyword.to_json())
        return {"code": 200, "status": "OK", "data": keywords_list}

    @auth.login_required()
    def post(self):
        data = self.parser.parse_args()
        keywords_list = eval(data["keywords"])  # keywords是一个列表的字符串
        operation = data["operation"]
        if operation.lower() == "add":  # 如果传入的参数是add，则添加keyword TODO 只能插入一次数据
            for keyword in keywords_list:
                keyword_to_add = UserKeywordModel(keyword=keyword, user_id=self.user_id)
                db.session.add(keyword_to_add)
            db.session.commit()
            return {"code": 201, "status": "Created"}
        elif operation.lower() == "delete":  # 如果传入的值是delete，则删除keyword
            for keyword in keywords_list:
                user_keyword_list = UserKeywordModel.query.filter(UserKeywordModel.user_id == self.user_id,
                                                                  UserKeywordModel.keyword == keyword).all()
                for user_key in user_keyword_list:
                    db.session.delete(user_key)
            db.session.commit()
            return {"code": 200, "status": "OK"}
        else:
            return {"code": 501, "status": "Not Implemented"}


class UserSubscriptionChannel(CORSResource, UserToken):
    def __init__(self):
        super().__init__()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("channel", type=int, required=True)

    @auth.login_required
    def post(self):
        data = self.parser.parse_args()
        channel = data["channel"]
        UserModel.query.filter_by(id=self.user_id).update({"channel": channel})
        db.session.commit()
        return {"code": 200, "status": "OK"}


class UserForgetPassword(CORSResource):
    # 获取忘记密码的验证码
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email")

    def get(self):
        data = self.parser.parse_args()
        email = data["email"]
        if _check_if_email_exists(email):  # 如果邮箱存在，则状态正常
            return {"code": 200, "status": "OK"}
        else:
            return {"code": 406, "status": "Not Acceptable: user doesn't exists"}

    def post(self):
        # 生成验证码发送给用户
        data = self.parser.parse_args()
        email = data["email"]
        if _check_if_email_exists(email=email):
            code = "".join([str(random.randint(0, 9)) for i in range(6)])
            # 发送邮件
            SendEmail(CodeEmailContent(code)).send_email(email)
            # 将验证码存在redis里
            pipeline = redis_client.pipeline()
            pipeline.set(email, code)
            pipeline.expire(email, 1800)  # 验证码30分钟过期
            pipeline.execute()
            return {"code": 200, "status": "OK"}
        else:
            return {"code": 406, "status": "Not Acceptable: user already exists"}


class UserForgetPasswordAuth(CORSResource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email")
        self.parser.add_argument("code")

    def get(self):
        data = self.parser.parse_args()
        email = data["email"]
        code = data["code"]
        # 从redis里获取该用户的验证码
        redis_code = redis_client.get(email).decode("utf-8")
        if code == redis_code:
            return {"code": 200, "status": "OK"}
        else:
            return {"code": 403, "status": "Forbidden"}


api.add_resource(News, "/api/news")
api.add_resource(UserRegister, "/api/user/register")
api.add_resource(UserLogin, "/api/user/login")
api.add_resource(UserEmailExist,"/api/user/email")
api.add_resource(UserSubscriptionKeyword, "/api/user/subscription/keyword")
api.add_resource(UserSubscriptionChannel, "/api/user/subscription/channel")
api.add_resource(UserForgetPassword, "/api/user/forget-password")
api.add_resource(UserForgetPasswordAuth, "/api/user/forget-password/auth")

if __name__ == '__main__':
    app.run(host="127.0.0.1", debug=True, port=5050)
    # print(_check_if_email_exists(email="1275021527@12qq.com"))