#! /bin/bash
apt-get update
# 安裝pip3
apt-get -y install python3-pip
# 安裝爬蟲所需套件
pip3 install scrapy scrapy_fake_useragent bs4 pymysql xxhash pytz
#export PATH="${PATH}:${HOME}/.local/bin

# 安裝git
apt-get -y install git

