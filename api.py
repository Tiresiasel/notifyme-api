from flask import jsonify, request
from notifyme import app, db, api
from notifyme.models import NewsModel, NewsKeywordModel, UserModel, UserKeywordModel
from flask_restful import Resource, reqparse
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from notifyme.error import *
from utils.auth import auth


class News(Resource):
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


class UserRegister(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True)
        self.parser.add_argument("password_hash", type=str, required=True)
        self.parser.add_argument("username", type=str, required=True)

    # 返回token字符串
    @staticmethod
    def _check_if_email_exists(email: str) -> bool:
        news_ids = UserModel.query.filter_by(email=email)
        if news_ids:
            return True
        else:
            return False

    def get(self):
        # 返回该邮箱是否存在
        data = self.parser.parse_args()
        email = data.get("email")
        if self._check_if_email_exists(email):
            return {"code": 406, "status": "Not Acceptable: user already exists"}
        else:
            return {"code": 200, "status": "OK"}

    def post(self):
        data = self.parser.parse_args()
        email = data.get("email")
        username = data.get("username")
        password_hash = data.get("password_hash")
        if self._check_if_email_exists(email=email):  # 如果该邮件在数据库内存在
            return {"code": 406, "status": "Not Acceptable: user already exists"}
        else:
            user_to_add = UserModel(username=username, email=email, password_hash=password_hash)
            db.session.add(user_to_add)
            db.session.commit()
            return {"code": 201, "status": "Created"}


class UserLogin(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("email", type=str, required=True)
        self.parser.add_argument("password_hash", type=str, required=True)

    @staticmethod
    def _generate_auth_token(uid: int, expiration=60 * 60 * 24):
        # 通过flask提供的对象，传入过期时间和flask的SECRET_KEY
        """生成令牌"""
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'uid': uid}).decode('ascii')

    @staticmethod
    def _check_if_password_hash_equals(email: str, password_hash: str) -> bool:
        db_password_hash = UserModel.query.with_entities(UserModel.password_hash).filter_by(email=email).first()[0]
        if db_password_hash == password_hash:
            return True
        else:
            return False

    def get(self):
        data = self.parser.parse_args()
        email = data.get("email")
        password_hash = data.get("password_hash")
        if self._check_if_password_hash_equals(email=email, password_hash=password_hash):
            uid = UserModel.query.with_entities(UserModel.id).filter_by(email=email).first()[0]
            return {"code": 200, "status": "OK", "data": {"token": self._generate_auth_token(uid)}}
        else:
            return {"code": 401, "status": "Unauthorized"}


class UserSubscription(Resource):
    def __init__(self):
        self.token = str(request.headers.get('Authorization')).split(' ')[-1]
        self.user_id = self._get_user_id_from_token()
        self.parser = reqparse.RequestParser()
        self.parser.add_argument("keywords", type=str, required=True)  # 前端传入list的字符串，后端解析
        self.parser.add_argument("operation", type=str, required=True)

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


class UserSubscriptionChannel(Resource):
    pass


api.add_resource(News, "/api/news")
api.add_resource(UserRegister, "/api/user/register")
api.add_resource(UserLogin, "/api/user/login")
api.add_resource(UserSubscription, "/api/user/token")
# api.add_resource()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
