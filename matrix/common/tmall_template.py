#!/usr/bin/python
#-*-coding:utf-8-*-

import sys
import random
import json

from scrapy.selector import HtmlXPathSelector
from scrapy import log 
from scrapy.log import ScrapyFileLogObserver

from lxml import etree

from matrix.common.filter import AlimamaFilter
from matrix.utils.select_result import list_first_item,strip_null,deduplication,clean_url
from matrix.utils.parse import get_item_id, get_itemlist_page, conv, get_item_prop, get_ratelist_page


"""
tamll template, parse item from tmall html
"""
class TmallTemplate(object):
    #匹配商品详情页中商品名称
    # name="title" value="全国-马尔代夫自由行蜜月旅行度假旅游一价全包酒店代理-香香假期"
    r_item_name = re.compile(r"\"title\" value=\"(.*)\"")
    #匹配商品列表页的下一页
    r_item_list_page = re.compile(r"J_SearchAsync next\" href=\"(.*)\"")
    #匹配商品列表页中商品名称、ID
    r_item_list_item = re.compile(r"detail.tmall.com/item.htm\?id=(\d+)&\" class=\"permalink\" style=\"\">\n+(.*)\n+</a>")
    #匹配商品列表页中商品的销量
    r_item_list_sell_count = re.compile(r"<em>(\d+)</em>")
    #匹配店铺ID
    r_shop_id = re.compile(r"shopid=\"(\d+)\"")
    #匹配商品详情页中init的地址 url
    r_init_url = re.compile(r"initApi\" : \"(.*)\",")
    #配置商品init url中的月成交数量
    r_sell_count = re.compile(r"sellCount\":(\d+)}")
    #匹配商品详情页中的商品ID
    r_item_id = re.compile(r"itemId:\"(\d+)\"")
    #匹配商品详情页中的sellerID
    r_seller_id = re.compile(r"sellerId:\"(\d+)\"")

    #匹配商品详情页的商品价格
    r_item_price = re.compile(r"defaultItemPrice\':\'(.*)\'")
    
    def __init__(self):
        print 'init tmall template'
        self.spider_filter = AlimamaFilter()
        
    def parse_detail(self, html, url, auction_url):
        item_name = get_item_prop(self.r_item_name, html, 1)
        item_id = get_item_prop(self.r_item_id, html, 1)
        seller_id = get_item_prop(self.r_seller_id, html, 1)
        price = get_item_prop(self.r_item_price, html, 1)
        shop_id = get_item_prop(self.r_shop_id, html, 1)  

        tags = self.spider_filter.create_item_tags(item_name)


        images = etree.HTML(html).xpath('//ul[@id="J_UlThumb"]/li/a/img/@src')
        # print "images:",images
        item_images = []
        for image in images:
            # origin_image_url = image.rstrip('_60x60.jpg')
            origin_image_url = image[0:image.index('_60x60.jpg')]
            item_images.append(origin_image_url)
            # print "origin_image_url:",origin_image_url
         # print 'item_images:',item_images   


        #crawl rate
        rate_url = self.default_rate_url.replace('$itemid$', item_id)   
        rate_url = rate_url.replace('$sellerid$', seller_id)
        rate_start_page = 1
        rate_url = rate_url.replace('$page$', str(rate_start_page))
        rate_count = self.get_item_rate_count(rate_url)

        if rate_count:
            print 'item_name:',item_name
            print 'item_id:',item_id
            print 'seller_id:',seller_id
            print 'item_price:',price
            print 'item_shop_id:',shop_id
            print 'action_url:',action_url
            print 'tags:',tags
            print 'item_images:',item_images
            print 'rate_page:',rate_url


            log.msg('item_name:'+item_name, log.INFO)
            log.msg('url:'+url, log.INFO)
            log.msg('item_id:'+item_id, log.INFO)
            log.msg('seller_id:'+seller_id, log.INFO)
            log.msg('item_price:'+price, log.INFO)
            log.msg('item_shop_id:'+shop_id, log.INFO)
            log.msg('action_url:'+action_url, log.INFO)
            log.msg('tags:'+tags, log.INFO)
            log.msg('item_images:'+''.join(item_images), log.INFO)
            log.msg('rate_page:'+rate_url, log.INFO)
    
        else:
            print '------------',item_id,item_name,'rate count = 0, abundon'
            log.msg('------------'+item_id+','+item_name+'rate count = 0, abundon', log.INFO)