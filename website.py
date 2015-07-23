__author__ = 'shaoqiu'

class WebSite:
    def __init__(self, status):
        self.status = status
        self.url = "http://qiushao.net"
        self.title = "一叶知秋"
        self.email = "360325900@qq.com"
        self.tags = []
        self.posts = []


class Post:
    def __init__(self):
        self.title = "title"
        self.tag = "tag"
        self.url = "url"
        self.markdown = ""