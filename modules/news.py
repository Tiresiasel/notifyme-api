import logging
import datetime
import urllib.parse
import uuid
from abc import abstractmethod, ABC

import requests
from bs4 import BeautifulSoup
from sqlalchemy.exc import IntegrityError, DataError

from modules.models import NewsModel, NewsKeywordModel
from modules import db
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt="%Y-%m-%d %H:%M:%S",
                    filename='../log/news.log',
                    filemode='w+')


class NewsBase(ABC):
    def __init__(self, base_url: str, path: str = None):
        self.base_url = base_url
        self.path = path
        self.raw_news_list = []
        self.parsed_news_list = []
        self.url = urllib.parse.urljoin(self.base_url, self.path)

    def _make_soup(self, params: dict) -> BeautifulSoup:
        res = requests.get(self.url, params).text  # request param
        soup = BeautifulSoup(res, features='lxml')
        return soup

    def get_and_update_all_news(self, keyword: str, limit_page: int = 100):
        self.get_all_news(keyword=keyword, limit_page=limit_page)
        self.update_all_news(keyword)

    def update_all_news(self, keyword: str):
        total_news = len(self.raw_news_list)
        for n, news in enumerate(self.raw_news_list):
            news_title = self.get_news_title(news)
            news_url = self.get_news_url(news)
            res = requests.get(news_url).text  # request param
            news_detail_soup = BeautifulSoup(res, features='lxml')
            news_content = self.get_news_content(news_detail_soup)
            news_description = self.get_news_description(news)
            news_cover = self.get_news_cover(news)
            news_source = self.get_news_source()
            news_type = self.get_news_type()
            news_spider_time = self.get_news_spider_time()
            news_publish_time = self.get_news_publish_time(news)
            news_source_code = self.get_news_source_code(news_url)
            news_uuid = self.get_news_uuid3(news_title).hex
            news_to_add = NewsModel(title=news_title, url=news_url, content=news_content,
                                    description=news_description, cover=news_cover,
                                    source=news_source, news_type=news_type, spider_time=news_spider_time,
                                    publish_time=news_publish_time,
                                    source_code=news_source_code, uuid=news_uuid)
            db.session.add(news_to_add)
            # news_keyword的关系表更新
            try:  # 耦合得太严重，回头把他拆开
                news_keyword_to_add = NewsKeywordModel(keyword=keyword, news_uuid=news_uuid)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logging.info(f"{news_title}已经在数据库内存在")
            except DataError:
                db.session.rollback()  # FIXME content格式不对的问题
                logging.info(f"{news_title}的字段格式错误")
            try:
                db.session.add(news_keyword_to_add)
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                logging.info(f"<{news_title}>已经在数据库内存在")
            logging.info(f"已添加<{news_title}>，完成进度{(n + 1) / total_news}")

    @abstractmethod
    def get_all_news(self, keyword: str, limit_page: int = 100):  # default 100 news
        pass

    @abstractmethod
    def get_news_title(self, news: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_news_url(self, news: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_news_content(self, news_page: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_news_description(self, news: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_news_cover(self, news: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_news_source(self) -> datetime:
        pass

    @abstractmethod
    def get_news_type(self) -> datetime:
        pass

    @staticmethod
    def get_news_spider_time() -> str:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @abstractmethod
    def get_news_publish_time(self, news: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_news_source_code(self, news: BeautifulSoup) -> datetime:
        pass

    @abstractmethod
    def get_author(self, news: BeautifulSoup) -> str:
        pass

    @staticmethod
    def get_news_uuid3(news_title: str):
        return uuid.uuid3(uuid.NAMESPACE_URL, news_title)


class ChainNews(NewsBase):
    def __init__(self, path: str = None):
        super().__init__(base_url="https://www.chainnews.com/", path=path)

    @abstractmethod
    def get_all_news(self, keyword: str, limit_page: int = 100) -> list:
        for i in range(limit_page):
            soup = self._make_soup({"q": keyword, "page": i + 1})
            self.raw_news_list.extend(soup.find_all("div", class_="feed-item feed-item-post"))

    def get_news_title(self, news: BeautifulSoup) -> datetime:
        news_title = news.find(class_="feed-post-title").text
        return news_title

    def get_news_url(self, news: BeautifulSoup) -> datetime:
        path = news.find(class_="feed-post-title").find("a").get("href")
        return urllib.parse.urljoin(self.base_url, path)

    def get_news_content(self, news: BeautifulSoup) -> datetime:
        news_content = news.find(class_="post-body column col-8 col-md-12").text
        return news_content

    def get_news_description(self, news: BeautifulSoup) -> datetime:
        news_description = news.find(class_="feed-post-summary").text
        return news_description

    def get_news_cover(self, news: BeautifulSoup) -> datetime:
        return None

    def get_news_source(self) -> datetime:
        return "ChainNews"

    @abstractmethod
    def get_news_type(self) -> datetime:
        pass

    def get_news_publish_time(self, news: BeautifulSoup) -> str:
        publish_time = news.find(class_="post-time").attrs["datetime"]
        publish_time_datetime = datetime.datetime.strptime(publish_time, "%Y-%m-%d %H:%M")
        publish_time_string = datetime.datetime.strftime(publish_time_datetime, "%Y-%m-%d %H:%M:%S")
        return publish_time_string

    def get_news_source_code(self, url) -> datetime:
        source_code = requests.get(url).text
        return source_code

    def get_author(self, news: BeautifulSoup) -> str:
        return None


class ChainNewSelected(ChainNews):
    def __init__(self):
        super().__init__(path="/search/selected/")

    def get_all_news(self, keyword: str, limit_page: int = 100) -> list:
        for i in range(limit_page):
            soup = self._make_soup({"q": keyword, "page": i + 1})
            self.raw_news_list.extend(soup.find_all("div", class_="feed-item feed-item-post"))

    def get_news_type(self) -> str:
        return "selected"


class ChainNewsArticle(ChainNews):
    def __init__(self):
        super(ChainNewsArticle, self).__init__(path="/search/article")

    def get_all_news(self, keyword: str, limit_page: int = 100) -> list:
        for i in range(limit_page):
            soup = self._make_soup({"q": keyword, "page": i + 1})
            self.raw_news_list.extend(soup.find_all("div", class_="feed-item feed-item-post"))

    def get_news_type(self) -> str:
        return "article"


class ChainNewsNews(ChainNews):
    def __init__(self):
        super(ChainNewsNews, self).__init__(path="/search/news")

    def get_all_news(self, keyword: str, limit_page: int = 100) -> list:
        for i in range(limit_page):
            soup = self._make_soup({"q": keyword, "page": i + 1})
            self.raw_news_list.extend(soup.find_all("div", class_="feed-item feed-item-news"))

    def get_news_type(self) -> str:
        return "news"


class ChainNewsPaper(ChainNews):  # TODO 完成链闻论文数据的获取
    def __init__(self):
        super(ChainNewsPaper, self).__init__(path="/search/news")

    def get_all_news(self, keyword: str, limit_page: int = 100) -> list:
        for i in range(limit_page):
            soup = self._make_soup({"q": keyword, "page": i + 1})
            self.raw_news_list.extend(soup.find_all("div", class_="feed-item feed-item-paper"))

    def get_news_type(self) -> str:
        return "paper"


if __name__ == '__main__':
    cn = ChainNewsNews()
    print(cn.get_and_update_all_news(keyword="bitcoin", limit_page=2))
