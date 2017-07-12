#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-12 下午10:53

'''单个价格的类信息'''
class PriceItem(object):
    def __init__(self,pricedate, coin,buy_price, buy_depth, sell_price, sell_depth):
        self.pricedate=pricedate
        self.coin=coin
        self.buy_price=buy_price
        self.buy_depth=buy_depth
        self.sell_price=sell_price
        self.sell_depth=sell_depth

'''保持一段时间内的价格列表，只保存最近一段时间，如一小时内的价格进行判断'''
class PriceBuffer(object):
    def __init__(self,priceitem=None):
        self.__priceitem=priceitem
        self.price_buffer=[]
        if  not priceitem:
            self.price_buffer.add(priceitem)
    '''增加新的价格列表'''
    def newprice(self,priceitem):
        self.price_buffer.add(priceitem)
        # TODO 需要增加逻辑来保证只保存最近一段时间的数据
        
if __name__ == '__main__':
    pass