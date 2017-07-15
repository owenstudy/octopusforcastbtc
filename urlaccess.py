#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.request
import random
import json

my_headers = [
    {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"}
    ]

def get_content(url):
    '''''
    @获取403禁止访问的网页
    '''
    global  my_headers
    randdom_header = random.choice(my_headers)
    req = urllib.request.Request(url=url,headers=randdom_header)

    content = urllib.request.urlopen(req).read()
    return content

# 把JSON数据放在对象中
class JSONObject:
    def __init__(self, d):
        self.__dict__ = d

def geturldata(url):
    # 打开链接获取返回数据
    req = get_content(url)
    # 返回的字节转换成字符串
    price = req.decode('utf8')
    # 转换为json格式的字符串
    str = json.dumps(price)
    #print(price)
    # 把json字符串转换成为python对象
    try:
        pricedata = json.loads(price, object_hook=JSONObject)
        return pricedata
    except:
        print('error price:%s'%price)
        return None


    #print(get_content(url))