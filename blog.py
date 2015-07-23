__author__ = "shaoqiu"

import tornado.template
import website

site = website.genSite("read")

loader = tornado.template.Loader("templates")

with open("index.html", 'wb') as fd:
    fd.write(loader.load("index.html").generate(site = website))
