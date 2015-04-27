#!/usr/bin/python
#-*-coding:utf-8-*-

# Scrapy settings for matrix project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

# Scrapy settings for matrix project
import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

BOT_NAME = 'matrix'

SPIDER_MODULES = ['matrix.spiders']
NEWSPIDER_MODULE = 'matrix.spiders'

DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_TIMEOUT = 15

COOKIES_ENABLED = True
COOKIES_DEBUG = True
RETRY_ENABLED = False
REDIRECT_ENABLED = True

 
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'manta (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.97 Safari/537.22 AlexaToolbar/alxg-3.1"
 
# DEFAULT_REQUEST_HEADERS={
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#     'Accept-Language': 'en',
#     'X-JAVASCRIPT-ENABLED': 'true',
# }
 
DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware':700,
}

#spider configs
SPIDER_FILTER_KEYWORDS = [
    '电子票', '船票',  
]

SPIDER_FILTER_URLS = [
    'http://kezhan.trip.taobao.com/',  
]

SPIDER_MATCHER_KEYWORDS = [
    '自由行', '潜水'
]  

REDIS_HOST = 'youhost'
REDIS_PORT = 6379

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'matrix (+http://www.yourdomain.com)'
