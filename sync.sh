#!/usr/bin/env bash
rsync --delete -avzP ./ shaoqiu@45.33.7.41:/var/www/qiushao.net/public_html --exclude=".git .idea __pycache__"
