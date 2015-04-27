#!/usr/bin/python
#-*-coding:utf-8-*-

import redis

class DupFilter:
    
    dup_key_taobao = 'dupefilter_t'

    REDIS_HOST = 'youhost'
    REDIS_PORT = 6379
    
    """Redis-based request duplication filter"""

    # def __init__(self, server, key):
    #     """Initialize duplication filter
    # 
    #     Parameters
    #     ----------
    #     server : Redis instance
    #     key : str
    #         Where to store fingerprints
    #     """
    #     self.server = server
    #     self.key = key
    def __init__(self):
        host = self.REDIS_HOST
        port = self.REDIS_PORT
        self.server = redis.Redis(host, port)

    @classmethod
    def from_settings(cls, settings):
        host = settings.get('REDIS_HOST', 'localhost')
        port = settings.get('REDIS_PORT', 6379)
        server = redis.Redis(host, port)
        # create one-time key. needed to support to use this
        # class as standalone dupefilter with scrapy's default scheduler
        # if scrapy passes spider on open() method this wouldn't be needed
        # key = "dupefilter:%s" % int(time.time())
        return cls(server, dup_key_taobao)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)
        
    def check_dup(value):
        if self.server.sismember(self.key, value):
            return True
        self.server.sadd(self.key, value)
        return False