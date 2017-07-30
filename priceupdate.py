#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 2017-07-13 1:34 AM
import logging;logging.basicConfig(level=logging.INFO,filename='pricehistory.log')
import datetime,time, operator
import const,common
import ordermanage,cointrans, publicparameters, ormmysql

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
    '''根据POOL 的比例得到校验的标准比例'''
    def __verify_std_rate(self):
        total_open_count = ormmysql.openordercount()
        open_rate = total_open_count / publicparameters.MAX_OPEN_ORDER_POOL

        if open_rate < 0.3:
            verify_rate = 0.35
        elif open_rate < 0.5:
            verify_rate = 0.45
        elif open_rate < 0.6:
            verify_rate = 0.65
        elif open_rate < 0.8:
            verify_rate = 0.75
        else:
            verify_rate = 0.85
        return verify_rate

    '''买入检查'''
    def buycheck(self,priceitem):
        # 暂停时间，买入时检查POOL的比例是不是超过一定的比例，会暂停以便平均分布
        pause_seconds = self.get_pause_seconds(priceitem)
        checkresult = False
        pauseresult = False
        verified_rate = self.get_forecast_rate()
        # 根据当前的仓位得到校验的标准比例
        verify_std_rate = self.__verify_std_rate()
        # 只有校验成功率超过一定比例才进行买入操作
        if verified_rate > verify_std_rate:
            checkresult = True
        else:
            checkresult = False
            return checkresult

        # 只有通过上面的预测比例后才进行比例的检查
        # 只有第一次通过预测验证后开始进入买入暂停阶段，本次买入成交
        if self.__pause_start_time is None:
            checkresult = True
        else:
            checkresult = False

        if self.__pause_start_time is None and pause_seconds > 0:
            # 暂停开始时间，只设置一次，然后开始检查，直到暂停结果
            self.__pause_start_time = datetime.datetime.now()
            if pause_seconds>self.__DEFAULT_BUY_PAUSE_SECONDS:
                print('{0}: {1}买入暂停，由于超过一半的比例，暂停{2}秒!'.format(common.get_curr_time_str(), priceitem.coin, pause_seconds))
        if self.__pause_start_time is not None:
            currtime = datetime.datetime.now()
            diff = currtime - self.__pause_start_time
            diffseconds = diff.seconds
            if diffseconds > pause_seconds:
                # 暂停结束
                self.__pause_start_time = None
                pauseresult = True
                if pause_seconds > self.__DEFAULT_BUY_PAUSE_SECONDS:
                    print('{0}: {1}买入暂停结束，共暂停{2}秒!'.format(common.get_curr_time_str(), priceitem.coin, pause_seconds))

        if pauseresult is True:
            checkresult = True
        # else:
        #     checkresult = False

        return checkresult
        pass

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
            if verified_rate > 0:
                print('{0}: verified rate:{1}'.format(priceitem.coin, verified_rate))
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
                if actual_profit_rate>publicparameters.SELL_PROFIT_RATE*1.2:
                    priceitem.price_buy_forecast_verify=True
                    priceitem.price_buy_forecast_verify_date=common.get_curr_time_str()
                    print('Verified result is correct: @%f'% newpriceitem.buy_price)
                    priceinfo = self.__save_price(priceitem)
                    # 执行实际的卖出操作
                    # sell to process in sell_check for all transaction
                    # trans_status = self.cointrans_handler.coin_trans(self.market, 'sell', newpriceitem.buy_price, priceitem)
                    trans_comments = "{0} -->Done: Verified Date: {1}"
                    # 打印出交易信息
                    print(trans_comments.format(priceinfo, common.get_curr_time_str()))
                    # print(priceinfo+'-->Done: trans status: @%s'%common.CommonFunction.get_curr_time())
                else:
                    priceitem.price_buy_forecast_verify=False

        
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
            print('取得价格列表时错误：{0}'.format(str(e)))
        return priceitem

'''监控价格的运行'''
class MonitorPrice(object):
    def __init__(self):
        # 控制的price buffer list
        self.__pricebuffer_list = {}
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
                        # 对超时的买单取消
                        # cointrans_data.cancle_ot_buy_order(publicparameters.CANCEL_DURATION)

                        cointrans_data.update_order_status()
                        cointrans_data.cancle_ot_buy_order(publicparameters.CANCEL_DURATION)
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
                        if len(forecast_list) > 0:
                            print('%s: verified:%d, total:%d for coin:%s'\
                                  %(common.CommonFunction.get_curr_time(), verified_count, len(forecast_list), coin_pair))
                    if runtime % 1000 == 0:
                        # 把预测中的列表输出出来
                        sorted_forecast_list = self.output_forecast_list(market, coin_list)
                except Exception as e:
                    print('处理{0}时出现错误:{1}'.format(coin_pair, str(e)))
        # return sorted_forecast_list
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
            unsorted_forecast_list.append({'coin':coin_pair, 'total':len(forecast_list), 'verified':verified_count, \
                                         'rate': round(verified_count/len(forecast_list),2)})
        # 对验证的结果进行排序，按验证率进行倒序
        sorted_forecast_list= sorted(unsorted_forecast_list, key=operator.itemgetter('rate'), reverse=True)

        print('---------------------final resut:--------------------')
        for forecast_item in sorted_forecast_list:
            if forecast_item.get('rate') > 0:
                print('%s: coin:%s, verified:%d, total:%d, rate:%f' \
                      % (common.CommonFunction.get_curr_time(), forecast_item.get('coin'), \
                         forecast_item.get('verified'), forecast_item.get('total'), forecast_item.get('rate') ))
            pass
        return sorted_forecast_list
    '''测试一段时间内的最优的可用币种列表'''
    def check_best_coin(self):

        # 针对btc38市场进行全部COIN进行查找， TODO 需要进行一个更进一步的排序，同等比例的情况下数量优先
        # sorted_forecast_list = self.monitor_coin_list('btc38', ['doge_cny','xrp_cny','etc_cny','xpm_cny'])

        sorted_forecast_list = self.monitor_coin_list('btc38', ['doge_cny', 'btc_cny', 'ltc_cny', 'xrp_cny', 'eth_cny', 'etc_cny', \
                                    'bts_cny', 'xlm_cny', 'nxt_cny', 'ardr_cny', 'blk_cny', 'xem_cny', \
                                    'emc_cny', 'dash_cny', 'xzc_cny', 'sys_cny', 'vash_cny', 'ics_cny', \
                                    'eac_cny', 'xcn_cny', 'ppc_cny', 'mgc_cny', 'hlb_cny', 'zcc_cny', \
                                    'xpm_cny', 'ncs_cny', 'ybc_cny', 'anc_cny', 'bost_cny', 'mec_cny', \
                                    'wdc_cny', 'qrk_cny', 'dgc_cny', 'bec_cny', 'ric_cny', 'src_cny', \
                                    'tag_cny', 'med_cny', 'tmc_cny'])
        return sorted_forecast_list

if __name__ == '__main__':

    # test monitor coin
    monitor_coin=MonitorPrice()
    x=monitor_coin.check_best_coin()

    # monitor_coin.monitor_coin_list('btc38',['doge_cny','btc_cny','ltc_cny', 'xrp_cny', 'eth_cny', 'etc_cny', \
    #                                         'bts_cny', 'xlm_cny', 'nxt_cny', 'ardr_cny', 'blk_cny', 'xem_cny', \
    #                                         'emc_cny', 'dash_cny', 'xzc_cny', 'sys_cny', 'vash_cny', 'ics_cny', \
    #                                         'eac_cny', 'xcn_cny', 'ppc_cny', 'mgc_cny', 'hlb_cny', 'zcc_cny', \
    #                                         'xpm_cny', 'ncs_cny', 'ybc_cny', 'anc_cny', 'bost_cny', 'mec_cny', \
    #                                         'wdc_cny', 'qrk_cny', 'dgc_cny', 'bec_cny', 'ric_cny', 'src_cny', \
    #                                         'tag_cny', 'med_cny', 'tmc_cny'])

    # now1=datetime.datetime.now()
    # time.sleep(2)
    # now2=datetime.datetime.now()
    # # print (now2-now1)
    # price1=PriceItem(now1,'doge',0.022,20000,0.024,30000)
    # price2=PriceItem(now2,'doge',0.025,35000,0.024,10000)
    # price3=PriceItem(now2,'doge',0.028,50000,0.024,4000)
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