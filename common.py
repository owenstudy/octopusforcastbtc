#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Owen_Study/owen_study@126.com'

import time,datetime
'''保存一些通用的函数'''

class CommonFunction(object):

    @classmethod
    #字符串对象，用于打印目的
    def get_curr_time(cls):
        currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return currtime
    # 字符串转换成日期类型
    @classmethod
    def strtotime(cls, datestr):
        return datetime.datetime.strptime(datestr,'%Y-%m-%d %H:%M:%S')
    #日期时间对象
    @classmethod
    def get_curr_date(cls):
        now=datetime.datetime.now()
        return now
    @classmethod
    #     日期转换成指定的字符串
    def datetimetostr(cls,dtime):
        return dtime.strftime('%Y-%m-%d %H:%M:%S')


# 字符串对象，用于打印目的
def get_curr_time_str():
    currtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    return currtime


#test
if __name__=='__main__':
    print(CommonFunction.get_curr_time())
    x='2017-07-16 08:19:46'
    datex=CommonFunction.strtotime(x)
    print(type(datex))