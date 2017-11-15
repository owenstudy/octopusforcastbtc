#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 2017-07-13 1:34 AM
import logging;logging.basicConfig(level=logging.INFO,filename='pricehistory.log')
import datetime,time, operator
import const,common
import ordermanage,cointrans, publicparameters, ormmysql
from dailysummary import DailySummary

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
        # 实际价格校验成立时间
        self.price_buy_forecast_verify_date=None
    '''打印显示对象的内容'''
    def __str__(self):
        priceinfo='|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(common.CommonFunction.get_curr_time().rjust(25),self.coin.rjust(6),\
                str(self.buy_price).rjust(10),str(self.buy_depth).rjust(20),str(self.sell_price).rjust(10),\
                str(self.sell_depth).rjust(20),str(self.price_buy_index).rjust(4),\
                str(self.price_buy_forecast).rjust(8),str(self.price_buy_forecast_verify).rjust(12))
        return priceinfo


'''保持一段时间内的价格列表，只保存最近一段时间，如一小时内的价格进行判断'''
class PriceBuffer(object):
    def __init__(self,market, priceitem=None, save_log_flag=True):
        # 保存执行过的价格列表
        self.price_buffer=[]
        # 保存那些预测为买入的记录
        self.price_forecast_list=[]
        # 市场
        self.market = market
        # 初始化常用的常量值
        self.__initconst()
        # 暂停开始时间
        self.__pause_start_time = None

        # 设置影响判断条件的公共参数
        # 上升趋势时，价格深度比较强的百分比
        # self.__PRICE_TREND_STRONG_PERCENTAGE=1.5
        # 买入趋势比较弱的百分比
        # self.__PRICE_TREND_WEAK_PERCENTAGE=0.6
        # 买入指数判断的时间范围，初始为按1小时内的价格进行判断,单位为秒
        # self.__PRICE_TREND_RANGE=3600
        # 价格buffer中保存的最大的价格记录数
        self.__PRICE_BUFF_MAX=2000
        # 止盈卖出的比例，用来确认预测买入的是不是符合要求
        # self.sell_profit_rate = 0.009
        # 默认的买入间隔，在50％之前
        self.__DEFAULT_BUY_PAUSE_SECONDS = 60
        #

        # 买入的标准指数
        # self.__BUY_INDEX_STANDARD=1.2

        # 调整公共参数, 设置默认的参数
        self.adjust_params(0.8, 0.6, 0.7, 3600)
        # 是否需要写log, 在进行研究的时候不需要写LOG
        self.save_log_flag = save_log_flag

        # 测试基准时间，用于从文件读取时设置一个基准时间进行循环测试
        self.basetime = None
        # 处理交易类初始化
        # self.cointrans_handler = cointrans.CoinTrans(market)
        self.cointrans_handler = cointrans.CoinTrans(market)

        if priceitem is not None:
            # 把处理好的价格加入到价格BUFFER列表
            self.newprice(priceitem)
        # 控制的price buffer list
        self.__pricebuffer_list = {}
        # 止损暂停秒数
        self.__pause_seconds_stop_lost = 0

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
    '''得到 TODO'''
    '''得到预测列表中的校验正确的比例,买入时参考这一比例'''
    def get_forecast_rate(self):
        # 判断当前预测的列表中哪些达到了预期的盈利目标
        verified_count = 0
        # 获取当前COIN中预测可以买入的列表
        forecast_list = self.price_forecast_list
        for forecast_item in forecast_list:
            if forecast_item.price_buy_forecast_verify is True:
                verified_count = verified_count + 1
        total_records = len(forecast_list)
        if total_records == 0:
            rate = 0
        else:
            rate = verified_count / len(forecast_list)

        return rate
    '''增加到达最大容量的限制，如果POOL池比例已经到达60％，则每次买入暂停一段时间，以确保不会在最快的时间把POOL用完，不能持续进行'''
    def get_pause_seconds(self, priceitem):
        # 当前已经存在的OPEN记录
        opencount = ormmysql.openordercount()
        # opencount = 51
        # POOL的比例
        pool_used_rate = round(opencount/ publicparameters.MAX_OPEN_ORDER_POOL,2)
        pause_seconds = 0
        # 超过50％后每增加一个百分比，则暂停1分钟，每前进10％则暂停1小时
        if pool_used_rate >= 0.9:
            # 暂停的秒数
            pause_seconds = 300*3
        elif pool_used_rate >= 0.8:
            pause_seconds = 240*3
        elif pool_used_rate >= 0.7:
            pause_seconds = 180*3
        elif pool_used_rate >= 0.6:
            pause_seconds = 120*3
        elif pool_used_rate >= 0.5:
            pause_seconds = 60*3
        else:
            # 50％之前每买入一次10秒后再进行买入
            pause_seconds = self.__DEFAULT_BUY_PAUSE_SECONDS
        return pause_seconds
    '''设置止损暂停买入的时间'''
    def get_pause_seconds_stop_lost(self):
        # 默认的止损暂停时间为600秒
        return 600
        pass

    '''根据POOL 的比例得到校验的标准比例'''
    def __verify_std_rate(self):
        total_open_count = ormmysql.openordercount()
        open_rate = total_open_count / publicparameters.MAX_OPEN_ORDER_POOL
        base_rate =0.25
        if open_rate < 0.3:
            verify_rate = base_rate
        elif open_rate < 0.5:
            verify_rate = base_rate + 0.1
        elif open_rate < 0.6:
            verify_rate = base_rate + 0.2
        elif open_rate < 0.8:
            verify_rate = base_rate + 0.3
        else:
            verify_rate = base_rate +0.45
        return verify_rate

    '''买入检查'''
    def buycheck(self,priceitem):
        # 暂停时间，买入时检查POOL的比例是不是超过一定的比例，会暂停以便平均分布
        pause_seconds = self.get_pause_seconds(priceitem)
        # 止损检查
        stop_lost_status = self.stop_lost(priceitem)
        # stop_lost_status = True
        if stop_lost_status is True:
            pause_seconds_stop_lost = self.get_pause_seconds_stop_lost()
            self.__pause_seconds_stop_lost= pause_seconds_stop_lost
            if pause_seconds_stop_lost > pause_seconds:
                pause_seconds = pause_seconds_stop_lost
        else:
            pause_seconds_stop_lost = 0

        checkresult = False
        verified_rate = self.get_forecast_rate()
        # 根据当前的仓位得到校验的标准比例
        verify_std_rate = self.__verify_std_rate()
        # 止损的暂停买入操作
        if stop_lost_status is True or self.__pause_start_time is not None:
            pause_finish = self.pause_buy(priceitem,self.__pause_seconds_stop_lost,self.__pause_seconds_stop_lost)
        else:
            pause_finish = None
        # 正在暂停的操作则停止买入操作
        if pause_finish is False:
            checkresult = False
            return checkresult
        # 只有校验成功率超过一定比例才进行买入操作
        if verified_rate > verify_std_rate and self.__pause_start_time is None:
            checkresult = True
            # 进行买入暂停操作检查
            self.pause_buy(priceitem, pause_seconds, 0)
        # 正在暂停的只需要检查是否结束
        elif verified_rate > verify_std_rate and self.__pause_start_time is not None:
            checkresult = False
            # 检查暂停操作是否结束
            self.pause_buy(priceitem,pause_seconds,0)
        else:
            checkresult = False

        return checkresult
        # # 只有通过上面的预测比例后才进行比例的检查
        # # 买入暂停检查
        # pause_finish = self.pause_buy(priceitem,pause_seconds,0)
        # # 只有正在暂停的，返回结果为假
        # if pause_finish is False:
        #     checkresult = False
        # return checkresult
        pass

    ''' 暂停买入'''
    # True 暂停完成， False正在暂停中， None无暂停
    def pause_buy(self, priceitem, pause_seconds, pause_seconds_stop_lost =0 ):
        pause_finish = None
        if self.__pause_start_time is None and pause_seconds>self.__DEFAULT_BUY_PAUSE_SECONDS:
            # 暂停开始时间，只设置一次，然后开始检查，直到暂停结果
            self.__pause_start_time = datetime.datetime.now()
            # 已经开始暂停了，但是还没有结束
            pause_finish = False
            if pause_seconds>self.__DEFAULT_BUY_PAUSE_SECONDS and pause_seconds_stop_lost == 0:
                print('{0}: {1}买入暂停，由于超过一半的比例，暂停{2}秒!'.format(common.get_curr_time_str(), priceitem.coin, pause_seconds))
            elif pause_seconds_stop_lost > 0:
                print( '{0}: {1}买入暂停，由于进行了止损操作，暂停{2}秒!'.format(common.get_curr_time_str(), priceitem.coin, pause_seconds))
        if self.__pause_start_time is not None:
            currtime = datetime.datetime.now()
            diff = currtime - self.__pause_start_time
            diffseconds = diff.seconds
            if diffseconds > pause_seconds:
                # 暂停结束
                self.__pause_start_time = None
                pause_finish = True
                self.__pause_seconds_stop_lost = 0
                if pause_seconds > self.__DEFAULT_BUY_PAUSE_SECONDS:
                    print('{0}: {1}买入暂停结束，共暂停{2}秒!'.format(common.get_curr_time_str(), priceitem.coin, pause_seconds))
            else:
                pause_finish = False
        return pause_finish

    '''更新BUFFER里面的订单状态'''
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
        # 对于需要买入的价格保存到买入列表
        if priceitem.price_buy_forecast is True:
            self.price_forecast_list.append(priceitem)
            # 执行买入操作
            verified_rate = self.get_forecast_rate()
            if verified_rate > 0.50:
                print('{0}>0.5: verified rate:{1}'.format(priceitem.coin, verified_rate))
            # 买入检查，看是不是可以买入
            checkresult = self.buycheck(priceitem)
            if checkresult is True:
                self.cointrans_handler.coin_trans(self.market, 'buy', priceitem.buy_price, priceitem)
            # 对最近一次的价格进行校验，判断最后一次的价格的预测买入是不是正确
        self.buyforecast_verify(priceitem)
        # 把最新的价格加入BUFFER列表中
        self.price_buffer.append(priceitem)
        # 每次把验证过后的价格保存到文件中供以后参考
        self.__save_price(priceitem)
        # TODO 需要增加逻辑来保证只保存最近一段时间的数据
        if len(self.price_buffer)>self.__PRICE_BUFF_MAX:
            # 移除最早的价格
            self.price_buffer.remove(self.price_buffer[0])

    # 处理未完成订单的止损操作
    def stop_lost(self, curr_pricitem):
        stop_lost_status = False
        open_order_list = ormmysql.openorderlist()
        for open_order in open_order_list:
            # 如果当前价格和买入价格小于止损的比例，则执行先取消订单再按当前价格的直接卖出操作
            curr_price = curr_pricitem.sell_price
            if curr_price / open_order.buy_price < (
                1 - publicparameters.STOP_LOST_RATE) and curr_pricitem.coin == open_order.coin:
                # if curr_pricitem.coin == open_order.coin:
                status = self.cointrans_handler.order_market.cancelOrder(open_order.sell_order_id, coin_code=curr_pricitem.coin)
                # #  TEST usage
                # status = const.CANCEL_STATUS_SUCC
                if status == const.CANCEL_STATUS_FAIL:
                    pass
                elif status == const.CANCEL_STATUS_SUCC:
                    # 更新订单的状态为取消
                    # ormmysql.updateorder(open_order)
                    # 重新卖出，以当前价卖出进行止损
                    sell_status = self.cointrans_handler.coin_trans(self.market, const.TRANS_TYPE_SELL, curr_price, open_order.priceitem)
                    # #  test only
                    # sell_status = True
                    # 止损卖出成功
                    if sell_status is True:
                        print("-------:(--------订单进行了止损操作,coin:{0},操作时间:{1}".format(open_order.coin,
                                                                                    common.get_curr_time_str()))
                        self.update_order_status()
                        stop_lost_status = True
                        pass
                    # 止损卖出失败，继续进行循环操作进行下一次的自动卖出
                    else:
                        pass
                    pass
        return stop_lost_status
    '''保存每次新增加的价格到LOG表中'''
    def __save_price(self,priceitem):
        if len(self.price_buffer)==1:
            # 第一条价格记录增加TITLE
            titlestr='|Price date|'.rjust(25) + ('Coin'.rjust(6)) + ('|buyPrice').rjust(10) + ('|buyDepth').rjust(10)
            titlestr=titlestr + ('|sellPrice').rjust(10) + ('|sellDepth').rjust(10) + ('|buyIndex').rjust(4) + ('|buyIndi').rjust(8)
            titlestr=titlestr + ('|buyVerifyIndi').rjust(12)
            #logging.info(titlestr)
        # priceitem=self.price_buffer[len(self.price_buffer)-2]
        pricetimestr=priceitem.pricedate.rjust(25)
        priceinfo='|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(pricetimestr,priceitem.coin.rjust(6),\
                str(priceitem.buy_price).rjust(10),str(priceitem.buy_depth).rjust(20),str(priceitem.sell_price).rjust(10),\
                str(priceitem.sell_depth).rjust(20),str(priceitem.price_buy_index).rjust(4),\
                str(priceitem.price_buy_forecast).rjust(8),str(priceitem.price_buy_forecast_verify).rjust(12))
        if self.save_log_flag is True:
            logging.info(priceinfo)
        return priceinfo

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
            # endtime=common.CommonFunction.strtotime('2017-07-16 23:08:31')
        starttime=endtime-datetime.timedelta(seconds=duration)
        # 在指定时间内所有价格的买入趋势占总体的比例,0~2之间的数字，加入预测因子后变成了0－3之间的数字
        total_buy_times=0
        total_price_number=0
        for priceitem in self.price_buffer:
            pricedate = common.CommonFunction.strtotime(priceitem.pricedate)
            if pricedate>starttime and pricedate<endtime:
                total_price_number=total_price_number+1
                if priceitem.price_trend_buy==const.PRICE_TREND_BUY_STRONG:
                    total_buy_times=total_buy_times+2
                elif priceitem.price_trend_buy==const.PRICE_TREND_BUY_NORMAL:
                    total_buy_times=total_buy_times+1
        # 增加预测准确性的比例因子
        verified_pass_rate = self.get_forecast_rate()

        if total_price_number==0:
            buy_index=0
        else:
            buy_index=total_buy_times/total_price_number
            # 预测准备性作为买入指数的一半权重进行计算
            buy_index = buy_index * (1+verified_pass_rate*0.5)
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
        endtime = common.CommonFunction.strtotime(newpriceitem.pricedate)
        starttime = endtime-datetime.timedelta(seconds=self.__PRICE_TREND_RANGE)
        for priceitem in self.price_buffer:
            pricedate = common.CommonFunction.strtotime(priceitem.pricedate)
            if pricedate>starttime and pricedate< endtime and priceitem.coin==newpriceitem.coin:
                # 已经预测过且得到验证的则不需要再继续进行
                if priceitem.price_buy_forecast_verify is True or priceitem.price_buy_forecast is False:
                    continue
                actual_profit_rate=(newpriceitem.buy_price-priceitem.buy_price)/priceitem.buy_price
                # 达到卖出条件则认为预测成功,预测价格变化是实际的一定比例，如0.8
                if actual_profit_rate>publicparameters.SELL_PROFIT_RATE*0.9:
                    priceitem.price_buy_forecast_verify=True
                    priceitem.price_buy_forecast_verify_date=common.get_curr_time_str()
                    # print('Verified passed:{0}:coin:{1},buy_price:{2},sell_price:{3}'.format(\
                    #     common.get_curr_time_str(),priceitem.coin,priceitem.buy_price,newpriceitem.buy_price))
                    # print('Verified result is correct: @%f'% newpriceitem.buy_price)
                    priceinfo = self.__save_price(priceitem)
                    # 执行实际的卖出操作
                    # sell to process in sell_check for all transaction
                    # trans_status = self.cointrans_handler.coin_trans(self.market, 'sell', newpriceitem.buy_price, priceitem)
                    trans_comments = "{0} -->Done: Verified Date: {1}"
                    # 打印出交易信息
                    # print(trans_comments.format(priceinfo, common.get_curr_time_str()))
                    # print(priceinfo+'-->Done: trans status: @%s'%common.CommonFunction.get_curr_time())
                else:
                    priceitem.price_buy_forecast_verify=False

        
        pass

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
            priceitem=PriceItem(common.get_curr_time_str(),coin,buy_price,buy_depth,sell_price,sell_depth)
        except Exception as e:
            print('取得[{1}]价格列表时错误：{0}'.format(str(e), coin_pair))
        return priceitem

'''监控价格的运行'''
class MonitorPrice(object):
    def __init__(self):
        # 控制的price buffer list
        self.__pricebuffer_list = {}
        # big fish实例
        self.bigfish = BigFish('ForecaseData.txt')
        # big fish生成列表
        # self.big_fish_list = []
        pass

    '''对某一个币种进行监听测试'''
    def monitor_coin(self,market, coin_pair):
        coinpricebuffer=self.__pricebuffer_list.get(coin_pair)
        # 如果COIN对应的price buffer不存在，则创建一个新的对象
        if coinpricebuffer is None:
            coinpricebuffer=PriceBuffer(market)
            self.__pricebuffer_list[coin_pair]=coinpricebuffer

        try:
            coinpricebuffer.adjust_params(0.95,1.2,0.7,3600)
            # 获取当前的市场价格
            newpriceitem = coinpricebuffer.getpriceitem(market, coin_pair)
            if newpriceitem is None:
                # print('获取价格失败:{0}'.format(coin_pair))
                return
            # 把当前的价格加入到价格列表
            coinpricebuffer.newprice(newpriceitem)
            # 最后一次的价格
            lastpriceitem = coinpricebuffer.price_buffer[len(coinpricebuffer.price_buffer)-2]
            if lastpriceitem.price_buy_forecast is True:
                # print(coinpricebuffer.price_buffer[len(coinpricebuffer.price_buffer)-2])
                pass
        except Exception as e:
            print(str(e))
        pass

    '''监控一个COIN列表'''
    def monitor_coin_list(self,market, coin_list):

        runtime = 0
        maxruntime = 10000
        while (True):
            time.sleep(5)
            for coin_pair in coin_list:
                try:
                    self.monitor_coin(market, coin_pair)
                    runtime = runtime + 1
                    # 很运行10次检查一下交易的状态
                    if runtime % 10 == 0:
                        cointrans_data = cointrans.CoinTrans(market)
                        # print(len(publicparameters.ORDER_LIST))
                        # 对OPEN订单进行卖出检查
                        cointrans_data.sell_check()
                        # 获取当前的价格
                        pricebuffer = PriceBuffer(market,save_log_flag=False)
                        newpriceitem = pricebuffer.getpriceitem(market, coin_pair)
                        # 止损检查，如果价格下降低于预定的止损值则执行卖出操作
                        # stop_lost_status = cointrans_data.stop_lost(newpriceitem)
                        # 对超时的买单取消
                        # cointrans_data.cancle_ot_buy_order(publicparameters.CANCEL_DURATION)

                        cointrans_data.update_order_status()
                        cointrans_data.cancle_ot_buy_order(publicparameters.CANCEL_DURATION)
                        # 增加把网站的成交记录保存到表中以便进行统计盈利情况
                        cointrans_data.save_aex_trans(coin_pair)
                    if runtime % 100 == 0:
                        print('Run {0}, 目前还未完成的订单有:{1}'.format(runtime, ormmysql.openordercount()))
                        # 获取当前COIN中预测可以买入的列表
                        forecast_list = self.__pricebuffer_list.get(coin_pair).price_forecast_list
                        verified_count = 0
                        # 判断当前预测的列表中哪些达到了预期的盈利目标
                        for forecast_item in forecast_list:
                            if forecast_item.price_buy_forecast_verify is True:
                                verified_count = verified_count + 1
                        # 输出每个COIN中预测的情况，多少达到了预期盈利
                        # if len(forecast_list) > 0:
                        #     print('%s: verified:%d, total:%d for coin:%s'\
                        #           %(common.CommonFunction.get_curr_time(), verified_count, len(forecast_list), coin_pair))
                    if runtime % 100 == 0:
                        # 把预测中的列表输出出来
                        sorted_forecast_list = self.output_forecast_list(market, coin_list)
                        # 大鱼检查
                        self.bigfish.get_big_fish_list()
                        each_big_fish_list =self.bigfish.big_fish_list
                        # 取每次列表的
                        # self.big_fish_list = self.big_fish_list + each_big_fish_list
                        # print('big fish list of all: {0}'.format(each_big_fish_list))
                        # big fish 列表写入
                        if len(each_big_fish_list) != 0:
                            bigfishfile = open('bigfish.txt','w')
                            bigfishfile.write('{0}:{1}\n'.format(common.get_curr_time_str(),each_big_fish_list))
                            bigfishfile.close()

                    # 增加定时输出报表的功能
                    if runtime % 1000 == 0:
                        daily_summary = DailySummary([market])
                        # 获取当前时间的余额信息
                        daily_summary.get_balance()


                except Exception as e:
                    print('处理{0}时出现错误:{1}'.format(coin_pair, str(e)))
        # return sorted_forecast_list
        pass
    '''检查BIG FISH并进行相应的处理'''
    def big_fish_process(self):
        each_big_fish_list = self.bigfish.get_big_fish_list()
        # 取每次列表的中第一个列表
        if len(each_big_fish_list) > 0:
            self.big_fish_list = self.big_fish_list + each_big_fish_list[0]
        print('big fish list of all: {0}'.format(self.big_fish_list))
        # big fish 列表写入
        if len(each_big_fish_list) != 0:
            bigfishfile = open('bigfish.txt', 'a')
            bigfishfile.write('{0}:{1}\n'.format(common.get_curr_time_str(), each_big_fish_list))
            bigfishfile.close()

        pass
    '''排序输出推荐买入列表的总体情况'''
    def output_forecast_list(self, market, coin_list):
        unsorted_forecast_list=[]
        for coin_pair in coin_list:
            self.monitor_coin(market, coin_pair)
            forecast_list = self.__pricebuffer_list.get(coin_pair).price_forecast_list
            verified_count = 0
            for forecast_item in forecast_list:
                if forecast_item.price_buy_forecast_verify is True:
                    verified_count = verified_count + 1
            if len(forecast_list) == 0:
                rate = 0
            else:
                rate = round(verified_count/len(forecast_list),2)
            unsorted_forecast_list.append({'coin':coin_pair, 'total':len(forecast_list), 'verified':verified_count, \
                                         'rate': rate })
        # 对验证的结果进行排序，按验证率进行倒序
        sorted_forecast_list= sorted(unsorted_forecast_list, key=operator.itemgetter('rate'), reverse=True)

        print('---------------------final resut:--------------------')
        for forecast_item in sorted_forecast_list:
            if forecast_item.get('rate') > 0:
                # Save to file to do analyze
                forecasedata = open('ForecaseData.txt','a')

                data = '{0}: coin:{1}, verified:{2}, forecase-total:{3}, rate:{4}\n'.format(\
                      common.get_curr_time_str(), forecast_item.get('coin'), \
                         forecast_item.get('verified'), forecast_item.get('total'), forecast_item.get('rate') )
                print(data)
                # save to file
                forecasedata.write(data)
                forecasedata.close()

            pass
        return sorted_forecast_list
    '''测试一段时间内的最优的可用币种列表'''
    def check_best_coin(self):

        # 针对btc38市场进行全部COIN进行查找， TODO 需要进行一个更进一步的排序，同等比例的情况下数量优先
        # sorted_forecast_list = self.monitor_coin_list('btc38', ['doge_cny','xrp_cny','etc_cny','xpm_cny'])
        coin_list =publicparameters.get_monitor_coin_list()
        self.monitor_coin_list('btc38',coin_list)
        # self.monitor_coin_list('btc38', ['doge_btc', 'ltc_btc', 'xrp_btc', 'eth_btc', 'etc_btc', \
        #                             # , 'xlm_btc', 'nxt_btc', 'ardr_btc', 'blk_btc', 'xem_btc', \
        #                             # 'emc_btc', 'dash_btc', 'xzc_btc', 'sys_btc', 'vash_btc', 'ics_btc', \
        #                             # 'eac_btc', 'xcn_btc', 'ppc_btc', 'mgc_btc', 'hlb_btc', 'zcc_btc', \
        #                             # 'xpm_btc', 'ncs_btc', 'ybc_btc', 'mec_btc', \
        #                             # 'wdc_btc', 'qrk_btc', 'ric_btc', \
        #                              'tmc_btc','bcc_btc','bts_btc'])
        # return sorted_forecast_list
'''捕捉大鱼，短时候内上升很快，有较大潜力强力上扬的COIN，买入一大笔霆投资'''
class BigFish( object ):
    def __init__(self, forecast_file):
        self.__forecast_file = forecast_file
        # 大鱼投资是默认投资的多少倍
        self.BIG_FISH_TIMES = 10
        # 大鱼投资时最低的预测成功率
        self.MIN_FORECAST_RATE = 0.25
        # 大鱼投资时最高的预测成功率，防止买入在顶端
        self.MAX_FORECAST_RATE = 0.55
        # 预测数据的时间范围，最近的多少秒,最近半小时
        self.FORECAST_RATE_DURATION = 1800
        # 最近的预测数据列表
        self.forecast_list = []
        # 大鱼列表
        self.big_fish_list = []

    '''从文件中读取最近的预测数据情况'''
    def __get_forecast_data(self):
        # 当前的系统时间
        currdate = datetime.datetime.now()
        # 预测数据的开始时间
        forecast_start_time = currdate - datetime.timedelta(seconds=self.FORECAST_RATE_DURATION)
        # 读取文件中的预测数据
        for indx, line in enumerate(open('ForecaseData.txt', 'r').readlines()):
            forecast_time = common.CommonFunction.strtotime(line.split(': ')[0])
            forecast_items = line.split(': ')[1].split(',')
            coin_pair = forecast_items[0].split(':')[1]
            verify_cnt = int(forecast_items[1].split(':')[1])
            rate = forecast_items[3].split(':')[1]
            rate = float(rate.split('\n')[0])
            forecast_item = {'coin_pair': coin_pair, 'date': forecast_time, 'verify_cnt': verify_cnt, 'rate': rate}
            if forecast_time > forecast_start_time:
                self.forecast_list.append(forecast_item)
    '''取得forecast列表中某个COIN的上升趋势比例'''
    def __get_forecast_uptrend_rate(self, coin_pair):
        coin_forecast_list = []
        for forecastitem in self.forecast_list:
            curr_coin_pair = forecastitem.get('coin_pair')
            if curr_coin_pair == coin_pair:
                coin_forecast_list.append(forecastitem)
        # 取出列表中指定COIN的列表数据并按时间进行排序
        sorted_coin_forecast_list = sorted(coin_forecast_list, key=operator.itemgetter('date'))
        uptrend_rate = self.__get_uptrend_rate(sorted_coin_forecast_list, trend_key='rate')

        return uptrend_rate
        pass
    '''读取预测列表中预测的成功率'''
    def get_succ_rate(self):
        coin_forecast = {}
        self.__get_forecast_data()
        for forecastitem in self.forecast_list:
            coin_pair = forecastitem.get('coin_pair')
            forecaserate = forecastitem.get('rate', 0)
            verify_cnt = forecastitem.get('verify_cnt')
            # 之前保存的数据
            if coin_forecast.get(coin_pair, -1) == -1:
                coin_forecast[coin_pair] = {'totalcnt':0, 'succcnt': 0}
            totalcnt = coin_forecast[coin_pair].get('totalcnt',0)
            succcnt = coin_forecast[coin_pair].get('succcnt', 0)
            totalcnt = totalcnt + 1
            coin_forecast[coin_pair]['totalcnt'] = totalcnt

            if forecaserate > self.MIN_FORECAST_RATE and forecaserate < self.MAX_FORECAST_RATE and verify_cnt > 10 :
                succcnt = succcnt + 1
                coin_forecast[coin_pair]['succcnt'] = succcnt
        # print('dict:{0}'.format(coin_forecast))
        '''字典转成列表'''
        forecast_list = []
        for coinpair in coin_forecast.keys():
            data = coin_forecast[coinpair]
            succcnt = data.get('succcnt')
            totalcnt = data.get('totalcnt')
            if totalcnt == 0:
                succrate = 0
            else:
                succrate = round (succcnt/totalcnt, 2)
            forecast_item = {'coin':coinpair, 'succcnt': succcnt, \
                             'totalcnt': totalcnt, 'succrate': succrate}

            forecast_list.append(forecast_item)
        # print('unsored list:{0}'.format(forecast_list))
        '''对结果进行排序，倒序排列'''
        sorted_forecast_list= sorted(forecast_list, key=operator.itemgetter('succrate'), reverse=True)

        print('sort:{0}'.format(sorted_forecast_list))
        return sorted_forecast_list
    '''得到大鱼的列表'''
    def get_big_fish_list(self):
        # big_fish_list = []
        sorted_forecast_list = self.get_succ_rate()
        for forecastitem in sorted_forecast_list:
            coin_pair = forecastitem.get('coin')
            succrate = forecastitem.get('succrate')
            succcnt = forecastitem.get('succcnt')

            # 只有数量大于一定数量的预测并且预测成功率在5成以上, 预测的上升趋势大于60％
            if succcnt > 10 and succrate > 0.5:
                # 上升的比例达到一定值才进入大鱼列表
                uptrend_rate = self.__get_forecast_uptrend_rate(coin_pair)
                if uptrend_rate > 0.3:
                    self.big_fish_list.append(forecastitem)
        print('big fish list: {0}'.format(self.big_fish_list))

    '''一个列表是不是上升趋势，上升趋势的百分比, 输入一个对象列表，和需要排序的KEY'''
    def __get_uptrend_rate(self, trendlist, trend_key):
        uptrend_rate = 0
        lastitemrate = None
        uptrend_cnt = 0
        if trendlist is None:
            return 0
        for trenditem in trendlist:
            currtrendrate = trenditem.get(trend_key)
            if trenditem.get(trend_key) is None:
                uptrend_rate = 0
                break
            # 第一次循环时忽略，只保留第一个值作为比较对象
            if lastitemrate is None:
                lastitemrate = trenditem.get(trend_key)
                continue
            else:
                if currtrendrate > lastitemrate:
                    uptrend_cnt = uptrend_cnt + 1
            # 保留当次的RATE作为下次比较
            lastitemrate = trenditem.get(trend_key)
        # 统计上升比例
        if len(trendlist) == 0:
            uptrend_rate = 0
        else:
            uptrend_rate = round(uptrend_cnt/len(trendlist),2)

        return uptrend_rate

        pass

    '''测试列表读取'''
    def test(self):

        testlist = [{'coin':'doge', 'rate':0.1}, {'coin':'doge', 'rate':0.11},{'coin':'doge', 'rate':0.12}, {'coin':'doge', 'rate':0.1}, {'coin':'doge', 'rate':0.12}]
        self.__get_uptrend_rate(testlist, 'rate')
        # self.__get_forecast_data()
        # print(str(self.forecast_list))
        # sorted_list = self.get_succ_rate()
        big_fish_list = self.get_big_fish_list()
        print('big fish list: {0}'.format(big_fish_list))

    pass
if __name__ == '__main__':
    # bigfish = BigFish('ForecaseData.txt')
    # bigfish.test()
    # test monitor coin
    monitor_coin=MonitorPrice()
    monitor_coin.check_best_coin()

    # monitor_coin.monitor_coin_list('btc38',['doge_cny','btc_cny','ltc_cny', 'xrp_cny', 'eth_cny', 'etc_cny', \
    #                                         'bts_cny', 'xlm_cny', 'nxt_cny', 'ardr_cny', 'blk_cny', 'xem_cny', \
    #                                         'emc_cny', 'dash_cny', 'xzc_cny', 'sys_cny', 'vash_cny', 'ics_cny', \
    #                                         'eac_cny', 'xcn_cny', 'ppc_cny', 'mgc_cny', 'hlb_cny', 'zcc_cny', \
    #                                         'xpm_cny', 'ncs_cny', 'ybc_cny', 'anc_cny', 'bost_cny', 'mec_cny', \
    #                                         'wdc_cny', 'qrk_cny', 'dgc_cny', 'bec_cny', 'ric_cny', 'src_cny', \
    #                                         'tag_cny', 'med_cny', 'tmc_cny','inf_cny'])

    now1=datetime.datetime.now()
    time.sleep(2)
    now2=datetime.datetime.now()
    # print (now2-now1)
    price1=PriceItem(now1,'doge',0.022,20000,0.024,30000)
    price2=PriceItem(now2,'doge',0.025,35000,0.024,10000)
    price3=PriceItem(now2,'doge',0.028,50000,0.024,4000)
    # price4=PriceItem(now2,'doge',0.030,50000,0.024,4000)
    # price5=PriceItem(now2,'doge',0.031,50000,0.024,4000)
    # price6=PriceItem(now2,'doge',0.032,50000,0.024,4000)
    # price7=PriceItem(now2,'doge',0.033,50000,0.024,4000)
    #
    # order_market=ordermanage.OrderManage('btc38')
    # price_depth=order_market.getMarketDepth('doge_cny')
    #
    # pricebuffer=PriceBuffer('btc38')
    # pricebuffer.get_pause_seconds(priceitem)
    # buyindi = False
    # while(not buyindi):
    #     buyindi = pricebuffer.buycheck()
    #     time.sleep(1)
    #
    # pricebuffer.monitor_coin_list('btc38',['doge_cny','btc_cny', 'ltc_cny'])
    # runtime=0
    # maxruntime=10000
    # while(runtime<maxruntime):
    #     time.sleep(5)
    #     try:
    #         runtime = runtime + 1
    #         pricebuffer.adjust_params(0.8,1.7,0.7,3600)
    #         newpriceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
    #         pricebuffer.newprice(newpriceitem)
    #         lastpriceitem = pricebuffer.price_buffer[len(pricebuffer.price_buffer)-2]
    #         if lastpriceitem.price_buy_forecast is True:
    #             print(pricebuffer.price_buffer[len(pricebuffer.price_buffer)-2])
    #     except:
    #         pass


    # pricebuffer.pricetrend(price2,pricebuffer.price_buffer)
    # pricebuffer.pricetrend_depth(price2,pricebuffer.price_buffer)

    #pricebuffer.newprice(price2)
    #pricebuffer.newprice(price3)
    #pricebuffer.newprice(price4)
    #pricebuffer.newprice(price5)
    #pricebuffer.newprice(price6)
    #pricebuffer.newprice(price7)

    # buy_index=pricebuffer.getbuyindex(5)
    # print('buy index:%s'%buy_index)
    # print(price2.price_trend_buy)
    # pass