#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-18 下午10:43

import const
'''对查找到的COIN进行交易，买入或者卖出'''

'''交易结构'''
class OrderItem(object):
    def __init__(self, coin, buy_price, buy_amount = 10):
        # 订单状态
        const.ORDER_STATUS_OPEN = 'Open'
        const.ORDER_STATUS_CLOSED = 'Closed'

        # 预测价格的信息
        self.priceitem = None
        # coin
        self.__coin = coin
        # 买入价格
        self.__buy_price = buy_price
        # 买入金额，默认为10RMB
        self.__buy_amount = buy_amount
        # 买入order_id
        self.__buy_order_id = None

        # 买入时间
        self.__buy_date = None
        # 买入UNIT
        self.__buy_units = None
        # 买入状态, Open, Closed
        self.__buy_status = None

        # 卖出相关
        # 卖出的order_id
        self.__sell_order_id = None
        # 卖出价格
        self.__sell_price = None
        # 卖出UNITS
        self.__sell_unts = None
        # 卖出金额
        self.__sell_amount = None
        # 卖出日期
        self.__sell_date = None
        # 卖出状态
        self.__sell_status = None

'''交易类'''
class CoinTrans(object):
    def __init__(self):
        # order 列表,所有交易的列表保存在这个列表中
        self.order_list = []
        # 最大的交易订单数，
        self.MAX_ORDER_COUNT = 100

        pass

    '''交易信息
    @trans_type   =='sell', 'buy'
    @coin
    @trans_units    交易UNIT
    @trans_price    交易价格
    @price_item     预测价格时的信息，用来进行对比
    '''
    def coin_trans(self, trans_type, coin, trans_units, trans_price, price_item):
        pass

    


if __name__ == '__main__':
    pass