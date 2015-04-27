#!/usr/bin/python
#-*-coding:utf-8-*-

import re
import chardet
import sys

def get_item_id(url):
    return url.split('=')[1]
    
def get_itemlist_page(url):
    pattern = re.compile(r'_fmu.a._0.t=\d+')
    match = pattern.search(url)
    if match:
        #output like : _fmu.a._0.t=13
         page_info = match.group()
         print page_info.split('=')[1]
         return page_info.split('=')[1]
    else:
        return '1'
        
def get_ratelist_page(url):
    pattern = re.compile(r'currentPage=\d+')
    match = pattern.search(url)
    if match:
        #output like : currentPage=13
         page_info = match.group()
         print page_info.split('=')[1]
         return page_info.split('=')[1]
    else:
        return '1'    
        
def conv(str):
    code =  chardet.detect(str)['encoding'].lower()
    if code =='utf-8':
        str = str.decode('utf-8')
    else:
        str = str.decode('gbk')
    return str    

def get_item_prop(regex, html, index):
    try:
        # self.r_shop_id.search(html).group(1)
        return regex.search(html).group(index)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        return ''