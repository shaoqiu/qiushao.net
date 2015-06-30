__author__ = "shaoqiu"

import os
import tornado.template
import website

website = website.WebSite("read")
for parent, dirlist, filelist in os.walk("posts"):
    website.tags.extend(dirlist)
    for post in filelist:
        post = os.path.splitext(post)[0]
        website.posts.append(os.path.join(parent, post))

loader = tornado.template.Loader("templates")

with open("index.html", 'wb') as fd:
    fd.write(loader.load("index.html").generate(site = website))
