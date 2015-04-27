#!/usr/bin/python
#-*-coding:utf-8-*-

import sys
import json
import random
from hashlib import md5
import urllib,urllib2,cookielib,re
from urllib import quote,unquote

from scrapy.selector import HtmlXPathSelector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.http import FormRequest, Request
from scrapy import log 
from scrapy.log import ScrapyFileLogObserver

from lxml import etree

from matrix.common.filter import AlimamaFilter
from matrix.store.redis import DupFilter
from matrix.utils.select_result import list_first_item,strip_null,deduplication,clean_url
from matrix.utils.parse import get_item_id, get_itemlist_page, conv, get_item_prop, get_ratelist_page

class TaobaoSpider(CrawlSpider):
    name = 'alimama'
    
    max_page_count = 3
    
    allowed_domains = ['taobao.com', 'tmall.com']
    start_urls = ['http://u.alimama.com/union/spread/selfservice/merchandisePromotion.htm?cat=&discountId=&pidvid=&_fmu.a._0.t=1&_fmu.a._0.pe=40&_fmu.a._0.l=&_fmu.a._0.so=_totalnum&c=&rewrite=&cat=&mid=&searchType=0&q=%BA%A3%B5%BA&_fmu.a._0.u=&_fmu.a._0.s=&_fmu.a._0.sta=&_fmu.a._0.end=&_fmu.a._0.st=&_fmu.a._0.en=&_fmu.a._0.star=0&loc=#']
    
    start_querys = [u'海南']
    
    '''
    params need used when cralwer working
    '''
    header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'}
    # headers = {'Accept-Charset':'GBK,utf-8;q=0.7,*;q=0.3',\
    #                 'Accept-Encoding':'gzip,deflate,sdch',\
    #                 'Accept-Language':'zh-CN,zh;q=0.8',\
    #                 'Cache-Control':'max-age=0',\
    #                 'Connection':'keep-alive',\
    #                 }
    login_data = {'logname':'',
                  'originalLogpasswd':'',
                  'logpasswd':'',
                  'proxy':'',
                  'redirect':'',
                  'style':''
                 }
    cookie_dict = {} 
    loginurl = 'https://www.alimama.com/member/minilogin_act.htm'
    
    spider_filter = AlimamaFilter()
    # dup_filter = DupFilter()

    default_next_page_link = '''http://u.alimama.com/union/spread/selfservice/merchandisePromotion.htm?cat=&discountId=&pidvid=&_fmu.a._0.t=$page$&_fmu.a._0.pe=40&_fmu.a._0.l=&_fmu.a._0.so=_totalnum&c=&rewrite=&cat=&mid=&searchType=&q=$query$&_fmu.a._0.u=&_fmu.a._0.s=&_fmu.a._0.sta=&_fmu.a._0.end=&_fmu.a._0.st=&_fmu.a._0.en=&_fmu.a._0.star=0&loc=# '''
    
    default_create_auction_url = 'http://u.alimama.com/union/spread/common/allCode.htm?specialType=item&auction_id='
    
    default_rate_url = 'http://rate.tmall.com/list_detail_rate.htm?spuId=0&order=0&append=0&content=1&itemId=$itemid$&sellerId=$sellerid$&currentPage=$page$'
    
    def __init__(self, *args, **kwargs):
        super(TaobaoSpider, self).__init__(*args, **kwargs)
        
        self.login_data['logname'] ='your account'
        self.login_data['originalLogpasswd'] = 'your password'
        self.login_data['logpasswd'] = md5(self.login_data['originalLogpasswd']).hexdigest()
        
        self.cookie_handle = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_handle))
        urllib2.install_opener(self.opener)
        

        #匹配跳转的页面是tmall还是taobao
        self.r_route_page_mark = re.compile(r"<h1 id=\"mallLogo\" >")
        
        ScrapyFileLogObserver(open("spider.log", 'w'), level=log.INFO).start()
        ScrapyFileLogObserver(open("spider_error.log", 'w'), level=log.ERROR).start()
        

    def login(self):    
        source = urllib2.urlopen('http://www.alimama.com/member/minilogin.htm').read()
        token_list = re.findall(r"input name='_tb_token_' type='hidden' value='([a-zA-Z0-9]+)'", source)
        self.login_data['_tb_token_'] = token_list[0] if token_list else ''
        self.login_data = urllib.urlencode(self.login_data)
        self.header['Referer'] = 'http://www.alimama.com/member/minilogin.htm'
        req = urllib2.Request(url=self.loginurl,data=self.login_data,headers=self.header)
        resp =urllib2.urlopen(req)
        html = resp.read()
        
        self.cookie_dict = {}
        for item in self.cookie_handle:  
            self.cookie_dict[item.name] = item.value
        # print self.cookie_dict
        
    def re_request(self, url):
        self.login()
        
        self.form_request(url)
        
    def start_requests(self):     
        self.login()        
        
        #for TaoBao, encode is GBK, need encode query word
        for i, q in enumerate(self.start_querys):
            query = quote(q.encode('GBK'))  
            
            # print 'agc$number$ddd'.replace('$number$','123')
            url = self.default_next_page_link.replace('$query$', query)     
            url = url.replace('$page$', '1')   
            print 'url=',url
            
            yield FormRequest(url, meta = {'cookiejar': i},\
                                    headers = self.header,\
                                    cookies = self.cookie_dict,\
                                    callback = self.parse_item)
        
        # for i, url in enumerate(self.start_urls):
        #     yield FormRequest(url, meta = {'cookiejar': i},\
        #                             headers = self.header,\
        #                             cookies = self.cookie_dict,\
        #                             callback = self.parse_item)
            # yield self.custom_form_request(url)
                                
    def custom_form_request(self, url):
        i = random.randint(1, 100)
        yield FormRequest(url, meta = {'cookiejar': i},\
                                headers = self.header,\
                                cookies = self.cookie_dict,\
                                callback = self.parse_item)
     
    def parse_item(self, response):  
        # if cookie expired, relogin 
        status = response.status
        if status == 302:
            self.re_request(response.url)
            return
        
        log.msg('parse_item url:'+ response.url, log.INFO)
         
        response_selector = HtmlXPathSelector(response)
                
        items = response_selector.select('//div[@class="list-info"]')
        auctions = response_selector.select('//p[@class="use-now"]/a/@auctionid').extract()
        # print items
                
        for i, item in enumerate(items):
            try:
                if item:    
                    detail_url = list_first_item(item.select('./a[2]/@href').extract())
                    item_name_ori = list_first_item(item.select('./a[2]/text()').extract())
                    # auctionid = list_first_item(item.select('.//p[@class="use-now"]/a/@auctionid').extract())
                    #in fact, auctionid equals itemid
                    auctionid = auctions[i]
                    # print '===================================================== item'
                    # print item
                    # print detail_url, item_name_ori
                    #depend on keywords, to decide continue crawl or abandon
                    item_id = get_item_id(detail_url)
                    # print item_id
                    if self.spider_filter.find_matcher_keyword(item_name_ori):
                    
                        # print detail_url, item_name_ori
                        # print item_id
                        print "detailurl=", detail_url
                        print 'auctionid=', auctionid
                        #check url md5
                        # if self.dup_filter.check_dup(item_id):
                            # print 'duplicate value:', item_id
                            #TODO: duplicate url need crawl back, then check items md5
                            # continue
                    
                        i = random.randint(1, 100)
                        detail_url = clean_url(response.url,detail_url,response.encoding)
                        '''
                            crawl taobao.com and tamll.com, don't need to login in, but tmall url would continue redirect,
                            so abandon scrapy, just use urllib2 to crawl detail item
                        '''
        
                        # self.header['Referer'] = detail_url
    #                     yield FormRequest(detail_url, meta = {'cookiejar': i},\
    #                                                   headers = self.header,\
    #                                                   cookies =  self.cookie_dict,\
    #                                                   # method= 'get',\
    #                                                   callback=self.parse_detail)
                        self.parse_http(detail_url, auctionid)
                          
                    elif self.spider_filter.find_filter_keyword(item_name_ori):
                        #TODO if rateCount > 0 || dealCount > 0, save to back db
                        detail_url = clean_url(response.url,detail_url,response.encoding)
                        self.parse_http(detail_url, auctionid)
                        # pass
                    
                    elif self.spider_filter.find_filter_url(detail_url):
                        #TODO if rateCount > 0 || dealCount > 0, save to back db
                        pass
                    
                    else:
                        pass
            except:
                print("parse item in item_list Unexpected error:", sys.exc_info()[1])
                
                      
        url = response.url    
        page_str = get_itemlist_page(url)
        page = int(page_str)
        page = page + 1
        
        if(page > self.max_page_count):
            return
            
        next_link = url.replace('_fmu.a._0.t='+page_str, '_fmu.a._0.t='+str(page))   

        if next_link:
            print 'next_link=',next_link
            log.msg('next_link:'+next_link, log.INFO)
            # next_link = clean_url(response.url,next_link,response.encoding)
            
            i = random.randint(1, 100)
            return Request(url=next_link, meta = {'cookiejar': i}, headers = self.header, cookies = self.cookie_dict, callback = self.parse_item)
            # return self.make_requests_from_url(next_link).replace(headers = self.header, cookies = self.cookie_dict,callback=self.parse_item)
      
    def parse_http(self, url, auctionid):
        req = urllib2.Request(url=url,headers=self.header)
        resp =urllib2.urlopen(req)
        #charset adapter
        html = conv(resp.read())
        
        #generate auction url
        auction_create_url = self.default_create_auction_url + auctionid
        auction_req = urllib2.Request(url=auction_create_url,headers=self.header)
        auction_html = conv(urllib2.urlopen(auction_req).read())
        auction_url_list = etree.HTML(auction_html).xpath('//textarea[@id="J_codeArea"]/text()')
        action_url = auction_url_list[0] if auction_url_list else ''
        
        # print html
        return self.parse_detail(html, url, action_url)
        
                                        

    def parse_detail(self, html, url, action_url):
        try:
            is_tamll_page = self.r_route_page_mark.search(html)
            #tmall page , use tmall template
            if is_tamll_page:
                # print "======================================== taobao path"
                # # item_url = hxs.select('//span[@id="J_ImgBooth"]/@src').extract()
                # item_price = hxs.select('//li[@id="J_StrPriceModBox"]//em[@class="tb-rmb-num"]/text()').extract()
                #         
                #         
                # item_name = hxs.select('//div[@class="tb-detail-hd"]/h3/text()').extract()
                # # item_region = list_first_item(info.select('./input[@na[1]/me="region"]/@value').extract())
                #         
                # print item_price,item_name
                
            #taobao page , use taobao template
            else:

        
                self.get_item_rate(rate_url)

                # [Request(url=rate_url ,callback=self.get_item_rate)]
                # [self.make_requests_from_url(rate_url).replace(callback=self.get_item_rate)]
        except:
            print("parse_detail Unexpected error:", sys.exc_info()[0])

    def get_item_rate_count(self, url):    
        req = urllib2.Request(url=url,headers=self.header)
        resp =urllib2.urlopen(req)
        #charset adapter
        html = conv(resp.read())
        
        #taobao API return no standard json, need trim
        #"  rateDetail":""
        len1 = len('"  rateDetail":')
        html = html[len1:len(html)]
        # print 'rate json body:',html
        rate_json = (json.loads(html))
        rate_list_json = {}
        if rate_json:
            rate_list_json = rate_json["rateList"]   
        # print rate_list_json   
        rate_len = len(rate_list_json)
        return rate_len
        
    def get_item_rate(self, url):    
        print '------------------------------------------------------ get item rate page'
        req = urllib2.Request(url=url,headers=self.header)
        resp =urllib2.urlopen(req)
        #charset adapter
        html = conv(resp.read())
        
        #taobao API return no standard json, need trim
        #"  rateDetail":""
        len1 = len('"  rateDetail":')
        html = html[len1:len(html)]
        # print 'rate json body:',html
        rate_list_json = (json.loads(html))["rateList"]   
        # print rate_list_json   
        rate_len = len(rate_list_json)
        if rate_len:   
            self.parse_rate_list(rate_list_json)
        else:
            #abandon
            return
        
        #print first rate page 
        page_str = get_ratelist_page(url)
        page = int(page_str)
        page = page + 1

        next_rate_url = url.replace('currentPage='+page_str, 'currentPage='+str(page))
        print 'next_rate_url:',next_rate_url
        # return self.get_item_rate(next_rate_url)
        # return [Request(url=page_url ,callback=self.get_item_rate)]
        
    def parse_rate_list(self, rate_list_json):
        if rate_list_json:
            for rate in rate_list_json:
                print 'rateContent:',rate["rateContent"]
                log.msg('rateContent:'+rate["rateContent"], log.INFO)