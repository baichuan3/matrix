#!/usr/bin/python
#-*-coding:utf-8-*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class MatrixItem(Item):
    # define the fields for your item here like:
    item_id = Field()
    item_name = Field()
    image_urls = Field()
    shop_id = Field()
    price = Field()
    tags = Field()
    item_from = Field()
    
    pass
