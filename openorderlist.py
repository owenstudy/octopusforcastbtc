#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__='Owen_Study/owen_study@126.com'


#open order的类，保存交易时的相关信息
class OpenOrderItem(object):
    def __init__(self,order_id,market, coin_code_pair,trans_type,trans_price, trans_unit, apply_date ):
        self.order_id=order_id
        self.market=market
        self.coin_code_pair=coin_code_pair
        self.trans_type=trans_type
        self.trans_price=trans_price
        self.trans_unit=trans_unit
        self.apply_date=apply_date

#test

if __name__=='__main__':
    open_order_item=OpenOrderItem(111,'bter','doge','sell',1.11,100,'2015-3-4')

    open_list=[]
    open_list.append(open_order_item)

    for open_order in open_list:
        print(open_order.order_id)

