from notifyme import app
from notifyme.models import NewsModel, NewsKeywordModel, UserModel
from flask_restful import Resource, Api, reqparse, fields

api = Api(app)

news_field = {
    "id": fields.Integer,
    "keyword": fields.String,
    "news_id": fields.Integer

}


class News(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('keyword', type=str, required=True)
        self.parser.add_argument('limit', type=str)
        # self.parser.add_argument("title", type=str)
        # self.parser.add_argument("url", type=str)
        # self.parser.add_argument("content", type=str)
        # self.parser.add_argument("description", type=str)
        # self.parser.add_argument("cover", type=str)
        # self.parser.add_argument("source", type=str)
        # self.parser.add_argument("spider_time", type=int)  # 时间戳(秒)
        # self.parser.add_argument("publish_time", type=int)  # 时间戳(秒)
        # self.parser.add_argument("source_code", type=str)

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
        return {"code": "200", "status": "success", "data": news_list}

    # def post(self):
    #     data = self.parser.parse_args()
    #     title = data.get("title")
    #     url = data.get("url")
    #     content = data.get("content")
    #     description = data.get("description")
    #     cover = data.get("cover")
    #     source = data.get("source")
    #     spider_time = data.get("spider_time")
    #     publish_time = data.get("publish_time")
    #     source_code = data.get("sourcecode")
    #
    #     news = NewsModel(title=title,url=url,content=content,description=description,cover = cover,
    #                      source=source,spider_time=spider_time,publish_time=publish_time,source_code=source_code,)


class User(Resource):
    # @staticmethod
    # def abort_if_email_exist(self, email): # email is unique
    #     email = db.query.filter_by(email = email ).first()
    #     if email:
    #         raise ValidationError(f"Email:{email} has already exited")
    #
    # def abort_if_user_does_not_exist(self, user):
    #     db.query.filter_by(user=user).first()

    def __init__(self):
        self.parse = reqparse.RequestParser()
        self.parse.add_argument('user', type=str, )

    def get(self, ):
        data = self.parser.parse_args()
        data.get("user")
        user = UserModel.query().all()
        return user

    def post(self):
        pass

    def delete(self):
        pass


api.add_resource(News, "/news/api")

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
