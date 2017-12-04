#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-4 下午9:42
# @Author  : Owen_study
# @Email   : owen_study@163.com
# @File    : pricemanage.py
# @Software: PyCharm
# ===============================================

import priceupdate
import ordermanage, common, config, time

'''保存各个市场的价格信息到文件中以方便后期的数据分析'''
'''目前支持的市场列表为WEX.NZ, AEX.COM(btc38)'''
class MarketPrice(object):
    def __init__(self, market_list, save_freq_seconds=5):
        self.__market_list = market_list
        self.__save_freq_seconds = save_freq_seconds
        self.__coin_list = config.price_monitor_coin_list.get('coinlist').split(',')

    # 生成价格列表
    '''从市场取得价格，返回一个价格明细'''
    def getpriceitem(self,market,coin_pair):
        try:
            order_market=ordermanage.OrderManage(market)
            price_depth=order_market.getMarketDepth(coin_pair)
            buy_depth=0
            sell_depth=0
            priceitem=None
            coin=coin_pair.split('_')[0]
            # use the sell price as buy_price
            buy_price=price_depth.sell[0][0]
            # use the buy orderprice as sell price
            sell_price=price_depth.buy[0][0]
            # 尝试列表中所有的买入和
            for buy_item in price_depth.buy:
                buy_depth=buy_depth+buy_item[1]
            for sell_item in price_depth.sell:
                sell_depth=sell_depth+sell_item[1]
            buy_depth=round(buy_depth,2)
            sell_depth=round(sell_depth,2)
            # 把价格日期保存成字符串
            priceitem=priceupdate.PriceItem(common.get_curr_time_str(),coin,buy_price,buy_depth,sell_price,sell_depth)
        except Exception as e:
            # print('取得[{1}]价格列表时错误：{0}'.format(str(e), coin_pair))
            return None
        return priceitem
    '''保存价格列表到文件中'''
    def savepricetofile(self):
        for market in self.__market_list:
            pricefile = open(market + '.txt', 'a')
            for coin_pair in self.__coin_list:
                price= self.getpriceitem(market,coin_pair)
                if price is not None:
                    pricefile.write(str(price)+'\n')
            pricefile.close()
    '''循环自动保存'''
    def start_price_auto_save(self):
        while(True):
            self.savepricetofile()
            # 每隔多少秒执行一次，防止执行速度过快导致网站异常
            time.sleep(self.__save_freq_seconds)

if __name__ == '__main__':
    pricemanage = MarketPrice(['wex','btc38'],5)
    pricemanage.start_price_auto_save()
    pass