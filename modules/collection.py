from abc import abstractmethod, ABC
from modules.models import NewsModel


class Collection(ABC):
    def __init__(self):
        pass 

    @abstractmethod()
    def _get_all_news_info(self):
        pass

    @abstractmethod
    def _insert_news_to_database(self):
        pass

    @abstractmethod
    def get_and_insert_news(self):
        pass


class PollingCollection(Collection):
    def __init__(self):
        super(PollingCollection, self).__init__()

    def _get_all_keywords_with_spider_date(self):
        NewsModel.query.with_entities(NewsModel.keyword).filter_by(
            news_uuid=news["uuid"]).all()

    def _get_all_news_info(self, max_page=None):
        pass

    def _insert_news_to_database(self):
        pass

    def get_and_insert_news(self):
        pass


class CustomizedCollection(Collection):
    def __init__(self):
        pass
