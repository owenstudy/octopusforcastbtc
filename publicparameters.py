#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-19 下午9:08

import cointrans

'''系统运行时需要用到的一些参数'''

# 每次交易的金额， RMB
TRANS_AMOUNT_PER_ORDER = 3
# 最大的交易池，即同时存在的最大OPEN订单数量
MAX_OPEN_ORDER_POOL = 10
# 卖出交易的止盈百分比
SELL_PROFIT_RATE = 0.012
# 价格rounding的位数,包括价格和交易单元
ROUNDING_PRICE={'doge': {'price': 5, 'unit': 0}, 'ltc': {'price': 2, 'unit': 2}, 'btc': {'price': 1, 'unit': 3}}

# 交易的公共对象，每次交易时都调用这个对象
ORDER_LIST = []

# 文件名称
# 还没有交易完成的文件
OPEN_TRANS_FILE = 'open_trans_file'
# 已经交易完成的文件名称
CLOSED_TRANS_FILE = 'closed_trans_file'


# 价格rounding规则
def rounding_price(coin):
    rounding_data = ROUNDING_PRICE.get(coin)
    if rounding_data == None:
        return 2
    else:
        return rounding_data.get('price', 2)
# UNIT的ROUNDING规则
def rounding_unit(coin):
    rounding_data = ROUNDING_PRICE.get(coin)
    if rounding_data == None:
        return 2
    else:
        return rounding_data.get('unit', 2)

if __name__ == '__main__':
    pass