__author__ = 'shaoqiu'

import os
import tornado.httpserver
import tornado.ioloop
import tornado.web
import website
import multiprocessing

def genSite(status):
    site = website.WebSite(status)
    posts = "posts"
    tags = os.listdir(posts)
    for tag in tags:
        if tag.startswith("."):
            continue
        files = os.listdir(os.path.join(posts, tag))
        if len(files) > 0:
            site.tags.append(tag)
            for post in files:
                post = os.path.splitext(post)[0]
                site.posts.append(os.path.join(posts, tag, post))
    # tag 按字典序排序
    site.tags.sort()
    # 文章按修改时间排序
    site.posts.sort(key=lambda post:os.stat(post + ".md").st_ctime, reverse=True)
    return site


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r"/login", LoginHandler),
            (r"/article", ArticleHandler),
            (r"/admin", AdminHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=False,
            cookie_secret="61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        print("get /")
        self.render("index.html", site=genSite("read"))


class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        user = self.get_argument("user", "")
        passwd = self.get_argument("password", "")
        if user == "shaoqiu" and passwd == "16889188":
            self.set_secure_cookie("user", user, expires_days=1)
            self.redirect("/admin")
        else:
            self.write("login failed")


class ArticleHandler(tornado.web.RequestHandler):
    def get(self):
        tag = self.get_argument("tag", "")
        title = self.get_argument("title", "")
        if tag == "":
            filepath = "about.md"
        else:
            filepath = "posts/" + tag + "/" + title + ".md"

        print("get " + filepath)
        with open(filepath, "r", encoding="utf-8") as fd:
            self.write(fd.read())

    def post(self):
        user = self.get_secure_cookie("user")
        if user.decode("utf-8") != "shaoqiu":
            print("cookie is out of time")
            self.write("cookie is out of time, please relogin")
            return

        operator = self.get_argument("operator", "")
        tag = self.get_argument("tag", "")
        title = self.get_argument("title", "")
        markdown = self.get_argument("markdown", "")
        if tag == "":
            filepath = "about.md"
        else:
            filepath = "posts/" + tag + "/" + title + ".md"

        if operator == "update":
            if not os.path.exists("posts/" + tag):
                os.makedirs("posts/" + tag)
            with open(filepath, 'w', encoding="utf-8") as fd:
                fd.write(markdown)
            os.system("./commit.sh update {0}".format(filepath))
        elif operator == "del":
            os.system("./commit.sh delete {0}".format(filepath))
        else:
            self.write("unkwon operator")


class AdminHandler(tornado.web.RequestHandler):
    def get(self):
        user = self.get_secure_cookie("user")
        if user.decode("utf-8") == "shaoqiu":
            self.render("index.html", site=genSite("write"))
        else:
            self.render("index.html", site=genSite("read"))


def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(9010)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
