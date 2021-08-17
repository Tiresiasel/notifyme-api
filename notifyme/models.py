from notifyme import db

class JSONComposer:
    def to_json(self):
        dic = self.__dict__
        if "_sa_instance_state" in dic:
            del dic["_sa_instance_state"]
        return dic

class UserModel(db.Model, JSONComposer):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user = db.Column(db.String(length=255), nullable=False, unique=True)
    email = db.Column(db.String(length=255), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=255),nullable=False)
    vip_level = db.Column(db.Integer)
    last_notify_time = db.Column(db.DateTime)
    channel = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __repr__(self):
        return f"User: {self.name}"


class NewsModel(db.Model, JSONComposer):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(length=255))
    url = db.Column(db.String(length=255))
    content = db.Column(db.String)
    description = db.Column(db.String)
    cover = db.Column(db.String)
    source = db.Column(db.String)
    spider_time = db.Column(db.DateTime)
    publish_time = db.Column(db.DateTime)
    source_code = db.Column(db.String)

    def __repr__(self):
        return f"News: {self.title}"


class NewsKeywordModel(db.Model, JSONComposer):
    __tablename__ = "news_keyword"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    keyword = db.Column(db.String)
    news_id = db.Column(db.Integer)

    def __repr__(self):
        return f"news_id: {self.news_id}, keyword_id: {self.keyword}"

    def to_json(self):  # ---------------------
        dic = self.__dict__
        if "_sa_instance_state" in dic:
            del dic["_sa_instance_state"]
        return dic

class UserKeywordModel(db.Model, JSONComposer):
    __tablename__ = "user_keyword"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer)
    keyword = db.Column(db.String)

if __name__ == '__main__':
    # 从news_keyword表中获取news的id
    news_id_list = []
    news_ids = NewsKeywordModel.query.with_entities(NewsKeywordModel.news_id) \
        .filter_by(keyword="a16z").all()
    news_id = list(map(lambda x: x[0], news_ids))
    news_id_list.extend(news_id)