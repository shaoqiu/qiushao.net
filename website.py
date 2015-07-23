__author__ = 'shaoqiu'

import os

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

def genSite(status):
    site = WebSite(status)
    posts = "posts"
    tags = os.listdir(posts)
    for tag in tags:
        if tag.startswith("."):
            continue
        files = os.listdir(os.path.join(posts, tag))
        if len(files) > 0:
            site.tags.append(tag)
            for postfile in files:
                post = Post()
                post.title = os.path.splitext(postfile)[0]
                post.tag = tag
                post.url = os.path.join(site.url, posts, tag, post.title) + ".html"
                site.posts.append(post)
    # tag 按字典序排序
    site.tags.sort()
    # 文章按修改时间排序
    site.posts.sort(key=lambda post:os.stat(os.path.join(posts, post.tag, post.title) + ".md").st_ctime, reverse=True)
    return site