#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-8 下午11:21
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : pricealert.py
# @Software: PyCharm
# ===============================================

import sms, ordermanage, json, time
import priceupdate,common
import pandas as pd

'''监测价格进行预警通知'''

class PriceAlert(object):
    def __init__(self, market_list, coin_pair_list):
        # 预警的上升和下降比例
        self.__alert_percent_up = 0.08
        self.__alert_percent_down = 0.10
        # 变化的时间范围，单位为小时
        self.__alert_duration = 2
        # 市场列表和COIN列表
        self.__market_list =market_list
        self.__coin_pair_list = coin_pair_list
        # 当前运行时的价格列表
        self.__price_list =[]
        self.__price_pd ={}


        pass
    '''是否上升到预定比例'''
    def match_alert_percent(self):
        # TODO
        pass
    '''当前的上升或者下降比例'''
    def get_change_percent(self):
        # TODO
        pass
    '''取价格信息'''
    '''从市场取得价格，返回一个价格明细'''
    def getprice(self, market, coin_pair):
        try:
            order_market = ordermanage.OrderManage(market)
            price_depth = order_market.getMarketDepth(coin_pair)
            buy_depth = 0
            sell_depth = 0
            priceitem = None
            coin = coin_pair.split('_')[0]
            # use the sell price as buy_price
            buy_price = price_depth.sell[0][0]
            # use the buy orderprice as sell price
            sell_price = price_depth.buy[0][0]
            # 尝试列表中所有的买入和
            for buy_item in price_depth.buy:
                buy_depth = buy_depth + buy_item[1]
            for sell_item in price_depth.sell:
                sell_depth = sell_depth + sell_item[1]
            buy_depth = round(buy_depth, 2)
            sell_depth = round(sell_depth, 2)
            # 把价格日期保存成字符串
            priceitem = priceupdate.PriceItem(common.get_curr_time_str(), coin, buy_price, buy_depth, sell_price,
                                              sell_depth)
            result = {"market":market, "coin_pair": coin_pair}
        except Exception as e:
            # print('取得[{1}]价格列表时错误：{0}'.format(str(e), coin_pair))
            return None
        return result
    '''把价格加入列表'''
    def add_new_price(self, priceitem):
        self.__price_pd = priceitem.get('market')
        # self.__price_list.append(priceitem)
        pass
    '''获取一次所有市场和所有监控COIN的新价格'''
    def one_round_price(self):
        for market in self.__market_list:
            for coin_pair in self.__coin_pair_list:
                newprice = self.getprice(market, coin_pair)
                if newprice is not None:
                    self.add_new_price(newprice)

        pass
    '''循环获取价格列表'''
    def loop_new_price(self):
        while(True):
            self.one_round_price()
            self.save_price_to_pandas()
            time.sleep(5)
    '''价格列表保存到pandas数据框中'''
    def save_price_to_pandas(self):
        for price in self.__price_list:
            pricepd = pd.DataFrame(price)
            print(pricepd)
            pass
        pass
pass

if __name__ == '__main__':
    pricealert = PriceAlert(['btc38'],['ltc_btc'])
    # pricealert.loop_new_price()
    df1 = pd.DataFrame({'market':['btc38'], 'coin_pair':['ltc_btc']})

    pass