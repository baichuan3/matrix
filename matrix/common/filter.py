#!/usr/bin/python
#-*-coding:utf-8-*-

class AlimamaFilter(object):
    # spider_filter_keywords = []
    # spider_filter_urls = []
    # spider_matcher_keywords = []
    
    spider_filter_keywords = [
        u'酒店', u'飞机票',
    ]

    spider_filter_urls = [
        u'http://kezhan.trip.taobao.com/',  
    ]

    spider_matcher_keywords = [
        u'自由行', u'潜水'
    ]
    
    test_keywords = [
        u'酒店', u'飞机票'
    ]

    # def __init__(self, spider_filter_keywords, spider_filter_urls, spider_matcher_keywords):
    #     self.spider_filter_keywords = spider_filter_keywords
    #     self.spider_filter_urls = spider_filter_urls
    #     self.spider_matcher_keywords = spider_matcher_keywords
    
    # def __init__(self, crawler):   
    #     self.spider_filter_keywords = crawler.settings.get('SPIDER_FILTER_KEYWORDS',[])
    #     self.spider_filter_urls = crawler.settings.get('SPIDER_FILTER_URLS',[])
    #     self.spider_matcher_keywords = crawler.settings.get('SPIDER_MATCHER_KEYWORDS',[])
    #     
    @classmethod
    def from_settings(cls, settings):
        spider_filter_keywords = settings.get('SPIDER_FILTER_KEYWORDS',[])
        spider_filter_urls = settings.get('SPIDER_FILTER_URLS',[])
        spider_matcher_keywords = settings.get('SPIDER_MATCHER_KEYWORDS',[])  
        
        return cls(spider_filter_keywords, spider_filter_urls, spider_matcher_keywords)  
        
    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)
        
    def find_matcher_keyword(self, word):
        print self.spider_matcher_keywords
        hint = False
        for matcher_keyword in self.spider_matcher_keywords:
            position = word.find(matcher_keyword) 
            if position > -1 :
                hint = True
            
            if hint:
                break
                
        return hint
                
    def find_filter_keyword(self, word):
        hint = False
        for filter_keyword in self.spider_filter_keywords:
            position = word.find(filter_keyword) 
            if position > -1 :
                hint = True
            
            if hint:
                break
                
        return hint
                
    def find_filter_url(self, url):
        hint = False
        for filter_url in self.spider_filter_urls:
            position = url.find(filter_url) 
            if position > -1 :
                hint = True
            
            if hint:
                break
                
        return hint
                
    def find_test_keyword(self, test_word):
        hint = False
        for test_keyword in self.test_keywords:
            print test_keyword, test_word
            position = test_word.find(test_keyword) 
            print position
            if position > -1 :
                hint = True
            
            if hint:
                break
                
        return hint
        
    def create_item_tags(self, word):
        tags = []
 
        for matcher_keyword in self.spider_matcher_keywords:
            position = word.find(matcher_keyword) 
            if position > -1 :
                tags.append(matcher_keyword)
                
        return ','.join(tags)
                
# testspider = MatrixFilter()
# ret = testspider.find_test_keyword('稻城亚丁机票')
# if ret:
#     print ret