#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 2017-07-13 1:34 AM
import logging;logging.basicConfig(level=logging.INFO,filename='pricehistory.log')
import datetime,time
import const,common
import ordermanage

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
        # 买入指数
        self.price_buy_index=None
        # 买入预估结果
        self.price_buy_forecast=None
        # 实际价格结果
        self.price_buy_forecast_verify=None
    '''打印显示对象的内容'''
    def __str__(self):
        priceinfo='|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(common.CommonFunction.get_curr_time().rjust(25),self.coin.rjust(6),\
                str(self.buy_price).rjust(10),str(self.buy_depth).rjust(20),str(self.sell_price).rjust(10),\
                str(self.sell_depth).rjust(20),str(self.price_buy_index).rjust(4),\
                str(self.price_buy_forecast).rjust(8),str(self.price_buy_forecast_verify).rjust(12))
        return priceinfo


'''保持一段时间内的价格列表，只保存最近一段时间，如一小时内的价格进行判断'''
class PriceBuffer(object):
    def __init__(self,priceitem=None, save_log_flag=True):
        self.price_buffer=[]
        # 初始化常用的常量值
        self.__initconst()

        # 设置影响判断条件的公共参数
        # 上升趋势时，价格深度比较强的百分比
        #self.__PRICE_TREND_STRONG_PERCENTAGE=1.5
        # 买入趋势比较弱的百分比
        #self.__PRICE_TREND_WEAK_PERCENTAGE=0.6
        # 买入指数判断的时间范围，初始为按1小时内的价格进行判断,单位为秒
        #self.__PRICE_TREND_RANGE=3600
        # 价格buffer中保存的最大的价格记录数
        self.__PRICE_BUFF_MAX=2000
        # 止盈卖出的比例，用来确认预测买入的是不是符合要求
        self.sell_profit_rate = 0.012
        #

        # 买入的标准指数
        # self.__BUY_INDEX_STANDARD=1.2

        # 调整公共参数, 设置默认的参数
        self.adjust_params(1.2, 1.5, 0.6, 3600)
        # 是否需要写log, 在进行研究的时候不需要写LOG
        self.save_log_flag = save_log_flag

        # 测试基准时间，用于从文件读取时设置一个基准时间进行循环测试
        self.basetime=None

        if priceitem!=None:
            # 把处理好的价格加入到价格BUFFER列表
            self.newprice(priceitem)

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

    # 调整一些公共参数，通过测试来得到最佳的参数
    def adjust_params(self, buy_index_standard=1.2, price_trend_strong_rate=1.5, price_trend_weak_rate=0.6, price_trend_range=3600):
        self.__PRICE_TREND_STRONG_PERCENTAGE = price_trend_strong_rate
        self.__PRICE_TREND_WEAK_PERCENTAGE = price_trend_weak_rate
        self.__PRICE_TREND_RANGE = price_trend_range
        self.__BUY_INDEX_STANDARD=buy_index_standard
    '''增加新的价格列表'''
    def newprice(self,priceitem):
        # 初始化新价格的上升下降趋势和买入卖出建议
        self.pricetrend(priceitem, self.price_buffer)
        self.pricetrend_depth(priceitem, self.price_buffer)
        # buy 指数
        buy_index=self.getbuyindex(self.__PRICE_TREND_RANGE)
        priceitem.price_buy_index=buy_index
        # 是否进行买入的预判
        priceitem.price_buy_forecast=self.buyforecast(buy_index)
        # 对最近一次的价格进行校验，判断最后一次的价格的预测买入是不是正确
        self.buyforecast_verify(priceitem)
        # 把最新的价格加入BUFFER列表中
        self.price_buffer.append(priceitem)
        # 每次把验证过后的价格保存到文件中供以后参考
        self.__save_price()
        # TODO 需要增加逻辑来保证只保存最近一段时间的数据
        if len(self.price_buffer)>self.__PRICE_BUFF_MAX:
            # 移除最早的价格
            self.price_buffer.remove(self.price_buffer[0])


    '''保存每次新增加的价格到LOG表中'''
    def __save_price(self):
        if len(self.price_buffer)==1:
            # 第一条价格记录增加TITLE
            titlestr='|Price date|'.rjust(25) + ('Coin'.rjust(6)) + ('|buyPrice').rjust(10) + ('|buyDepth').rjust(10)
            titlestr=titlestr + ('|sellPrice').rjust(10) + ('|sellDepth').rjust(10) + ('|buyIndex').rjust(4) + ('|buyIndi').rjust(8)
            titlestr=titlestr + ('|buyVerifyIndi').rjust(12)
            #logging.info(titlestr)
        priceitem=self.price_buffer[len(self.price_buffer)-2]
        priceinfo='|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(common.CommonFunction.get_curr_time().rjust(25),priceitem.coin.rjust(6),\
                str(priceitem.buy_price).rjust(10),str(priceitem.buy_depth).rjust(20),str(priceitem.sell_price).rjust(10),\
                str(priceitem.sell_depth).rjust(20),str(priceitem.price_buy_index).rjust(4),\
                str(priceitem.price_buy_forecast).rjust(8),str(priceitem.price_buy_forecast_verify).rjust(12))
        if self.save_log_flag is True:
            logging.info(priceinfo)

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
                if newpriceitem.buy_depth / newpriceitem.sell_depth > self.__PRICE_TREND_STRONG_PERCENTAGE:
                    buy_weight=2
                else:
                    buy_weight=1
            elif newpriceitem.buy_depth<last_price_item.buy_depth:
                if newpriceitem.buy_depth/last_price_item.buy_depth<self.__PRICE_TREND_WEAK_PERCENTAGE:
                    buy_weight=-2
                else:
                    buy_weight=-1
            else:
                buy_weight=0

            if newpriceitem.sell_depth<last_price_item.sell_depth:
                if newpriceitem.sell_depth/last_price_item.sell_depth<self.__PRICE_TREND_WEAK_PERCENTAGE:
                    sell_weight=2
                else:
                    sell_weight=1
            elif newpriceitem.sell_depth>last_price_item.sell_depth:
                if newpriceitem.sell_depth/last_price_item.sell_depth>self.__PRICE_TREND_STRONG_PERCENTAGE:
                    sell_weight=-2
                else:
                    sell_weight=-1
            else:
                sell_weight=0

            # 根据权重进行判断买入卖出趋势
            total_weight=buy_weight+sell_weight
            # print('总共的买入卖出权重:%d'%total_weight)
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
            return newpriceitem
    # 得到指定时间内买入指数,默认是当前系统时间之间指定秒数的价格，0－2之间的数字，越高越建议买入
    def getbuyindex(self, duration):
        # 没有价格时返回指数为0
        if len(self.price_buffer)==0:
            return 0
        if self.basetime==None:
            endtime=datetime.datetime.now()
        else:
            endtime=self.basetime
            # endtime=common.CommonFunction.strtotime('2017-07-16 01:08:19')
        starttime=endtime-datetime.timedelta(seconds=duration)
        # 在指定时间内所有价格的买入趋势占总体的比例,0~2之间的数字
        total_buy_times=0
        total_price_number=0
        for priceitem in self.price_buffer:
            if priceitem.pricedate>starttime and priceitem.pricedate<endtime:
                total_price_number=total_price_number+1
                if priceitem.price_trend_buy==const.PRICE_TREND_BUY_STRONG:
                    total_buy_times=total_buy_times+2
                elif priceitem.price_trend_buy==const.PRICE_TREND_BUY_NORMAL:
                    total_buy_times=total_buy_times+1
        if total_price_number==0:
            buy_index=0
        else:
            buy_index=total_buy_times/total_price_number
        return round(buy_index,2)

    # 买入预估结果，True 买入，False不买入
    def buyforecast(self,buy_index):
        # TODO 可能需要加入更多的逻辑来判断是否买入
        if buy_index>= self.__BUY_INDEX_STANDARD:
            return True
        else:
            return False
    '''实际买入的记录是不是符合预期的结果'''
    def buyforecast_verify(self, newpriceitem):
        if len(self.price_buffer)==0:
            newpriceitem.price_buy_forecast_verify = False
            return
        # 判断当前之前一段时间的预测买入是不是达到了卖出条件，如果达到说明预期结果正确
        endtime = newpriceitem.pricedate
        starttime = endtime-datetime.timedelta(seconds=self.__PRICE_TREND_RANGE)
        
        pass

    # 实际是否买入更新，根据新的实际价格得到是不是要买入，更新实际的情况，作为对预判的检查
    def buyforecast_verifyX(self,newpriceitem):

        if len(self.price_buffer)==0:
            newpriceitem.price_buy_forecast_verify = False
            return

        last_price_item = self.price_buffer[len(self.price_buffer) - 1]
        # 只有预估的价格是买入时，如果新的价格是上升的，说明当时预估的结果是正确的，其它的则说明不正确
        if last_price_item.price_buy_forecast is True and newpriceitem.buy_price > last_price_item.buy_price:
            last_price_item.price_buy_forecast_verify = True
        elif last_price_item.price_buy_forecast is False and newpriceitem.buy_price < last_price_item.buy_price:
            last_price_item.price_buy_forecast_verify = True
        else:
            last_price_item.price_buy_forecast_verify = False
    '''从市场取得价格，返回一个价格明细'''
    def getpriceitem(self,market,coin_pair):
        order_market=ordermanage.OrderManage(market)
        price_depth=order_market.getMarketDepth(coin_pair)
        buy_depth=0
        sell_depth=0

        coin=coin_pair.split('_')[0]
        buy_price=price_depth.buy[0][0]
        sell_price=price_depth.sell[0][0]
        # 尝试列表中所有的买入和
        for buy_item in price_depth.buy:
            buy_depth=buy_depth+buy_item[1]
        for sell_item in price_depth.sell:
            sell_depth=sell_depth+sell_item[1]
        buy_depth=round(buy_depth,2)
        sell_depth=round(sell_depth,2)
        priceitem=PriceItem(datetime.datetime.now(),coin,buy_price,buy_depth,sell_price,sell_depth)
        return priceitem

if __name__ == '__main__':


    now1=datetime.datetime.now()
    time.sleep(2)
    now2=datetime.datetime.now()
    print (now2-now1)
    price1=PriceItem(now1,'doge',0.022,20000,0.024,30000)
    price2=PriceItem(now2,'doge',0.025,35000,0.024,10000)
    price3=PriceItem(now2,'doge',0.028,50000,0.024,4000)
    price4=PriceItem(now2,'doge',0.030,50000,0.024,4000)
    price5=PriceItem(now2,'doge',0.031,50000,0.024,4000)
    price6=PriceItem(now2,'doge',0.032,50000,0.024,4000)
    price7=PriceItem(now2,'doge',0.033,50000,0.024,4000)

    order_market=ordermanage.OrderManage('btc38')
    price_depth=order_market.getMarketDepth('doge_cny')

    pricebuffer=PriceBuffer()
    runtime=0
    maxruntime=10000
    while(runtime<maxruntime):
        time.sleep(5)
        try:
            runtime = runtime + 1
            pricebuffer.adjust_params(0.8,1.7,0.7,3600)
            newpriceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
            pricebuffer.newprice(newpriceitem)
            print(pricebuffer.price_buffer[len(pricebuffer.price_buffer)-2])
        except:
            pass


    pricebuffer.pricetrend(price2,pricebuffer.price_buffer)
    pricebuffer.pricetrend_depth(price2,pricebuffer.price_buffer)

    #pricebuffer.newprice(price2)
    #pricebuffer.newprice(price3)
    #pricebuffer.newprice(price4)
    #pricebuffer.newprice(price5)
    #pricebuffer.newprice(price6)
    #pricebuffer.newprice(price7)

    buy_index=pricebuffer.getbuyindex(5)
    print('buy index:%s'%buy_index)
    print(price2.price_trend_buy)
    pass