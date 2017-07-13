#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 2017-07-13 1:34 AM

import const

'''单个价格的类信息'''
class PriceItem(object):
    def __init__(self,pricedate, coin,buy_price, buy_depth, sell_price, sell_depth):
        self.pricedate=pricedate
        self.coin=coin
        self.buy_price=buy_price
        self.buy_depth=buy_depth
        self.sell_price=sell_price
        self.sell_depth=sell_depth
        # 价格趋势只有放在价格列表中才会设置值
        self.price_trend=None
        # 价格趋势的深度，H,M,L三种,在价格列表比较后进行设置
        self.trend_depth=None
        # 买卖建议趋势
        self.price_trend_buy=None
        self.price_trend_sell=None


'''保持一段时间内的价格列表，只保存最近一段时间，如一小时内的价格进行判断'''
class PriceBuffer(object):
    def __init__(self,priceitem=None):
        self.price_buffer=[]
        # 初始化常用的常量值
        self.__initconst()
        if priceitem!=None:
            # 把处理好的价格加入到价格BUFFER列表
            self.price_buffer.append(priceitem)

    # 设置常用常量列表
    def __initconst(self):
        # 价格趋势常量
        const.PRICE_TREND_UP=1      # 上升
        const.PRICE_TREND_DOWN=-1   # 下降
        const.PRICE_TREND_NORMAL=0  # 持平
        # 价格趋势深度常量,暂时没用
        const.PRICE_TREND_DEPTH_HIGH='H'        # 比较强烈，上升或者下降强度
        const.PRICE_TREND_DEPTH_MEDIUM='M'      # 一般情况
        const.PRICE_TREND_DEPTH_LOW='L'         # 比较不推荐，上升时的可能性小，下降时的力量也不大
        # 买入建议选项
        const.PRICE_TREND_BUY_STRONG='SB'       # 强烈建议买入
        const.PRICE_TREND_BUY_NORMAL='B'        # 建议买入，趋势不太明显
        const.PRICE_TREND_BUY_REJECTED='RB'     # 不建议买入
        # 卖出建议选项
        const.PRICE_TREND_SELL_STRONG='SS'      # 强烈建议卖出
        const.PRICE_TREND_SELL_NORMAL='S'       # 建议卖出，趋势不明显
        const.PRICE_TREND_SELL_REJECTED='RS'    # 不建议卖出，目前买入趋势非常的明显


    '''增加新的价格列表'''
    def newprice(self,priceitem):
        # 初始化新价格的上升下降趋势和买入卖出建议
        self.pricetrend(priceitem, self.price_buffer)
        self.pricetrend_depth(priceitem, self.price_buffer)
        # 把最新的价格加入BUFFER列表中
        self.price_buffer.append(priceitem)
        # TODO 需要增加逻辑来保证只保存最近一段时间的数据

    '''得到上升还是下降的趋势'''
    # 价格趋势，每次价格进入后都进行比较前一次得出结论，1上升，0持平，-1,下降
    def pricetrend(self,newpriceitem, pricelist):
        # TODO
        if len(pricelist)==0:
            # 初始化第一个价格为0
            newpriceitem.price_trend=const.PRICE_TREND_NORMAL
        else:
            # 取最近的价格记录进行比较
            last_price_item=pricelist[len(pricelist)-1]
            # 判断价格趋势，根据买入价进行判断
            if newpriceitem.buy_price>last_price_item.buy_price:
                newpriceitem.price_trend = const.PRICE_TREND_UP
            elif newpriceitem.buy_price==last_price_item.buy_price:
                newpriceitem.price_trend = const.PRICE_TREND_NORMAL
            else:
                newpriceitem.price_trend = const.PRICE_TREND_DOWN
        pass
    # 价格趋势的深度和买入进出建议
    def pricetrend_depth(self,newpriceitem,pricelist):
        if len(pricelist)==0:
            # 初始化第一个价格深度
            newpriceitem.price_trend_buy=const.PRICE_TREND_BUY_NORMAL
            newpriceitem.price_trend_sell=const.PRICE_TREND_SELL_NORMAL

        else:
            #price_trend = self.pricetrend(newpriceitem, pricelist)
            # 取最近的价格记录进行比较
            last_price_item = pricelist[len(pricelist) - 1]

            if newpriceitem.buy_depth>last_price_item.buy_depth:
                # 强烈建议买入,价格上升并且买入量远大于卖出
                if newpriceitem.buy_depth / newpriceitem.sell_depth > 1.5:
                    buy_weight=2
                else:
                    buy_weight=1
            elif newpriceitem.buy_depth<last_price_item.buy_depth:
                if newpriceitem.buy_depth/last_price_item.buy_depth<0.6:
                    buy_weight=-2
                else:
                    buy_weight=-1
            else:
                buy_weight=0

            if newpriceitem.sell_depth<last_price_item.sell_depth:
                if newpriceitem.sell_depth/last_price_item.sell_depth<0.6:
                    sell_weight=2
                else:
                    sell_weight=1
            elif newpriceitem.sell_depth>last_price_item.sell_depth:
                if newpriceitem.sell_depth/last_price_item.sell_depth>1.5:
                    sell_weight=-2
                else:
                    sell_weight=-1
            else:
                sell_weight=0

            # 根据权重进行判断买入卖出趋势
            total_weight=buy_weight+sell_weight
            print('总共的买入卖出权重:%d'%total_weight)
            if total_weight>2:
                newpriceitem.price_trend_buy = const.PRICE_TREND_BUY_STRONG
                newpriceitem.price_trend_sell = const.PRICE_TREND_SELL_REJECTED
            elif total_weight>=0:
                newpriceitem.price_trend_buy = const.PRICE_TREND_BUY_NORMAL
                newpriceitem.price_trend_sell = const.PRICE_TREND_SELL_NORMAL
            elif total_weight<0:
                newpriceitem.price_trend_buy = const.PRICE_TREND_BUY_REJECTED
                if total_weight<-2:
                    newpriceitem.price_trend_sell = const.PRICE_TREND_SELL_STRONG
                else:
                    newpriceitem.price_trend_sell = const.PRICE_TREND_SELL_NORMAL

if __name__ == '__main__':
    price1=PriceItem('day1s1','doge',0.022,20000,0.024,30000)
    price2=PriceItem('day1s2','doge',0.025,35000,0.024,10000)
    pricebuffer=PriceBuffer(price1)
    #pricebuffer.newprice(price2)
    pricebuffer.pricetrend(price2,pricebuffer.price_buffer)
    pricebuffer.pricetrend_depth(price2,pricebuffer.price_buffer)
    print(price2.price_trend_buy)
    pass