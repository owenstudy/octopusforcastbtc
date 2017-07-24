#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 7/24/17 1:14 PM

from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.sql.expression import Cast
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

# 表的属性描述对象
metadata = MetaData()


'''注释'''

import cointrans
if __name__ == '__main__':
    # -*- coding: utf-8 -*-
    class Site(object):
        def __init__(self):
            self.title = 'jb51 js code'
            self.url = 'http://www.jb51.net'

        def list_all_member(self):
            for name, value in vars(self).items():
                print('%s=%s' % (name, value))


    class OrderItem(object):
        def __init__(self, market, coin):

            # 预测价格的信息
            self.priceitem = None
            # market
            self.market = market
            # coin
            self.coin = coin
            # 买入价格
            self.buy_price = None
            # 买入金额，默认为10RMB
            self.buy_amount = None
            # 买入order_id
            self.buy_order_id = None

            # 买入时间
            self.buy_date = None
            # 买入UNIT
            self.buy_units = None
            # 买入状态, Open, Closed
            self.buy_status = None

            # 卖出相关
            # 卖出的order_id
            self.sell_order_id = None
            # 卖出价格
            self.sell_price = None
            # 卖出UNITS
            self.sell_units = None
            # 卖出金额
            self.sell_amount = None
            # 卖出日期
            self.sell_date = None
            # 卖出状态
            self.sell_status = None

        '''转换成字符保存'''

        # TODO
        def __repr__(self):
            order_detail_format = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}|{10}|{11}|{12}|{13}|\n'
            if self.sell_amount is not None:
                profit_amount = round(self.sell_amount - self.buy_amount, 2)
            else:
                profit_amount = ''
            return order_detail_format.format(self.market.rjust(8), self.coin.rjust(6), profit_amount,
                                              self.buy_order_id, self.buy_date, \
                                              self.buy_status, self.buy_price, self.buy_amount, self.buy_units,
                                              self.sell_order_id, \
                                              self.sell_date, self.sell_status, self.sell_amount, self.sell_units)

        # 打印出来字符
        def __str__(self):
            return self.__repr__()

        def list_all_member(self):
            for name, value in vars(self).items():
                print('%s=%s' % (name, value))
    if __name__ == '__main__':
        site = OrderItem('btc38','doge')
        site.list_all_member()