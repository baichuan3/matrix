#!/usr/bin/python
#-*-coding:utf-8-*-

__author__ = 'liukoo'
import urllib,urllib2,cookielib,re
from hashlib import md5
class alimama:
    def __init__(self):

        self.header = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36'}
        self.cookie_handle = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie_handle))
        urllib2.install_opener(self.opener)

    def login(self,username,passwd):
        login_data = {
            'logname':'',
            'originalLogpasswd':'',
            'logpasswd':'',
            'proxy':'',
            'redirect':'',
            'style':''
        }
        login_data['logname'] =username
        login_data['originalLogpasswd'] =passwd
        login_data['logpasswd'] = md5(login_data['originalLogpasswd']).hexdigest()
        source = urllib2.urlopen('http://www.alimama.com/member/minilogin.htm').read()
        token_list = re.findall(r"input name='_tb_token_' type='hidden' value='([a-zA-Z0-9]+)'", source)
        login_data['_tb_token_'] = token_list[0] if token_list else ''
        loginurl = 'https://www.alimama.com/member/minilogin_act.htm'

        login_data = urllib.urlencode(login_data)
        self.header['Referer'] = 'http://www.alimama.com/member/minilogin.htm'
        try:
            req = urllib2.Request(url=loginurl,data=login_data,headers=self.header)
            resp =urllib2.urlopen(req)
            html = resp.read()
            # print "html: ", html.decode('utf-8')
            
            cookie_str = ''
            for item in self.cookie_handle:  
                cookie_str = cookie_str + item.name+'='+item.value+';'
                
            lenght = len(cookie_str)
            if lenght:
                cookie_str = cookie_str[0: lenght-1]
            print cookie_str
            
            cookie_dict = '{'
            for item in self.cookie_handle:  
                cookie_dict = cookie_dict + '\'' + item.name+'\': '
                if item.value:
                    cookie_dict = cookie_dict + '\''+item.value+'\''
                cookie_dict = cookie_dict + ','
            lenght = len(cookie_dict)
            if lenght:
                cookie_dict = cookie_dict[0: lenght-1]
            cookie_dict = cookie_dict + '}'
            print cookie_dict;
                
                
            if str(resp.url).find('success')!=-1:
                return True
        except Exception,e:
            print e
            return False

    def getUrl(self,url):
        try:
            item_id = re.search(r"id=(\d+)",url)
            item_id = item_id.group(1)
            html = urllib2.urlopen('http://u.alimama.com/union/spread/common/allCode.htm?specialType=item&auction_id='+item_id).read()
            rule = re.compile(r"var clickUrl = \'([^\']+)")
            return rule.search(html).group(1)
        except Exception,e:
            print e
            return False

#example
ali = alimama()
if ali.login('your account','your password'):
    url = ali.getUrl('http://item.taobao.com/item.htm?spm=a1z10.1.w4004-1205618817.6.Evkf6O&id=19322457214')
    if url:
        print 'getUrl:'
    else:
        print 'nothing'
else:
    print 'please login'
