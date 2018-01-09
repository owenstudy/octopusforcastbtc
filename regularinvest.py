#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-23 下午2:49
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : regularinvest.py
# @Software: PyCharm
# ===============================================
# 定期投资的交易

import config, ormmysql, common, datetime, pricealert, const, publicparameters
import cointrans, ordermanage, time, mymoneysummary
'''根据参数定义,自动进行买入和卖出操作'''
class RegularInvest(object):
    def __init__(self, market):
        self.__market = market
        # 定期投资的相关参数
        self.__regular_param = config.regular_invest_param
        # 每次买入的金额
        self.__trans_amount_per_trans = self.__regular_param.get('buy_amt')
        # 每次买入的时间
        self.__buy_time = self.__regular_param.get('buy_time')
        # 买入的频率,以小时为单位
        self.__buy_freq = self.__regular_param.get('buy_freq')
        # 一个COIN的总共投资上限
        self.__buy_max_amt = self.__regular_param.get('buy_max_amt')
        # 止盈比例
        self.__sell_profit_rate = self.__regular_param.get('sell_profit_rate')
        # 止损比例
        self.__stop_lost_rate = self.__regular_param.get('stop_lost_rate')
        # 操作的coin list
        self.__coin_list = self.__regular_param.get('coin_list').split(',')
        # 订单状态
        const.ORDER_STATUS_OPEN = 'open'
        const.ORDER_STATUS_CLOSED = 'closed'
        const.ORDER_STATUS_CANCEL = 'cancelled'
        const.TRANS_TYPE_BUY='buy'
        const.TRANS_TYPE_SELL='sell'
        # 取消订单状态
        const.CANCEL_STATUS_SUCC = 'success'
        const.CANCEL_STATUS_FAIL= 'fail'
        # 市场的交易处理器
        self.order_market = ordermanage.OrderManage(market)
    '''获取止盈比例'''
    def get_sell_profit_rate(self,coin_pair):
        default_sell_profit_rate = self.__regular_param.get('sell_profit_rate').get('default')
        sell_profit_rate = self.__regular_param.get('sell_profit_rate').get(coin_pair, default_sell_profit_rate)
        return sell_profit_rate
    '''自动买入操作'''
    def regular_buy(self, coin_pair):
        # 买入的标志
        buy_indi = self.regular_buy_indi(coin_pair)
        if buy_indi is True:
            # 保存当前的帐户余额快照
            mymoneysummary.gen_money_summary()
            pricealert_forecast = pricealert.PriceAlert(self.__market, self.__coin_list)
            # 当前的价格信息
            currpriceitem = pricealert_forecast.getpriceitem(self.__market, coin_pair)
            # 执行买入操作
            self.coin_trans(self.__market, const.TRANS_TYPE_BUY, currpriceitem.buy_price,currpriceitem)
            pass
        pass
    '''是否符合自动买入的条件'''
    def regular_buy_indi(self,coin_pair):
        last_trans_date = ormmysql.get_last_invest_date(coin_pair)
        # 没有交易记录则默认为可以买入
        if last_trans_date.get('last_trans_date') is None:
            result = True
            return result
        # 如果存在 则判断是不是符合买入条件
        last_trans_date = common.CommonFunction.strtotime(last_trans_date.get('last_trans_date'))
        result = False
        if last_trans_date is not None:
            # 根据参数计算下一次要操作的时间
            next_trans_date = last_trans_date + datetime.timedelta(seconds=self.__buy_freq*3600)
            currdate = datetime.datetime.now()
            if currdate > next_trans_date:
                # 符合买入条件
                result = True
                pass
        else:
            result = True
        return result
        pass
    '''止盈卖出检查'''
    def sell_check(self, coin_pair):
        regular_summary = ormmysql.get_regular_invest_summary(coin_pair)
        # 如果没有帐户则不进行卖出检查,只有先买入后才进行卖出检查
        if regular_summary is None:
            return

        pricealert_forecast = pricealert.PriceAlert(self.__market, self.__coin_list)
        # 当前的价格信息
        currpriceitem = pricealert_forecast.getpriceitem(self.__market, coin_pair)
        total_unit_balance = regular_summary.get('unit_balance')
        total_invest_amount = regular_summary.get('unit_amount')
        actual_amount = regular_summary.get('unit_balance')*currpriceitem.sell_price
        # 清空帐户后会出现金额为0的情况,需要排除检查
        if total_invest_amount>0:
            # 达到止盈的比例则执行卖出
            sell_profit_rate = self.get_sell_profit_rate(coin_pair)
            if actual_amount/total_invest_amount - 1 >= sell_profit_rate:
                self.coin_trans(self.__market, const.TRANS_TYPE_SELL, currpriceitem.sell_price, currpriceitem)
            # 止损检查
            elif actual_amount/total_invest_amount - 1 <= self.__stop_lost_rate*-1:
                # 临时把每次的交易金额设置为卖出的总金额
                # origi_trans_amount_per_trans = self.__trans_amount_per_trans
                # self.__trans_amount_per_trans = actual_amount
                # 把所有的买入都卖出
                self.coin_trans(self.__market, const.TRANS_TYPE_SELL, currpriceitem.sell_price, currpriceitem)
                # 恢复买入的默认买入金额
                # self.__trans_amount_per_trans = origi_trans_amount_per_trans
                pass
        # 更新帐户的估值信息
        if currpriceitem is not None:
            ormmysql.update_invest_estivalue(coin_pair, currpriceitem)

        pass
    '''自动开始买入和卖出循环'''
    def run_regular_invest(self):
        while(True):
            for coin_pair in self.__coin_list:
                try:
                    # 循环进行卖出和买入检查
                    self.regular_buy(coin_pair)
                    self.sell_check(coin_pair)
                    # 每10秒执行一次检查操作
                    time.sleep(10)
                    pass
                except Exception as e:
                    print('处理:{0}时发生错误:{1}'.format(coin_pair,str(e)))
        pass
    # 判断是不是满足买入或者卖出条件
    def check_trans_indi(self, coin_pair):
        regular_summary = ormmysql.get_regular_invest_summary(coin_pair)
        if regular_summary is None:
            return True
        # 已经买入的最大上限则停止买入
        total_unit_amount = regular_summary.get('unit_amount')
        mk_type = coin_pair.split('_')[1]
        # 不同币种有不同的最大值
        buy_max_amt = self.__regular_param.get('buy_max_amt').get(mk_type)

        if total_unit_amount >= buy_max_amt:
            return False
        return True
        pass
    '''交易信息
    @market ==btc38, bter
    @trans_type   =='sell', 'buy'
    @trans_price    交易价格
    @price_item     预测价格时的信息，用来进行对比
    '''
    def coin_trans(self, market, trans_type, trans_price, price_item):
        coin = price_item.coin
        coin_pair = price_item.coin_pair
        # coin_pair = coin+'_btc'

        # 判断是不是满足交易的条件，不满足则退出不进行交易
        if trans_type == const.TRANS_TYPE_BUY:
            if self.check_trans_indi(coin_pair) is False:
                # print('{0}:不符合买入条件，可能是超过买入数量上限或者比例上限'.format(coin))
                return False

        # 对价格和交易单位进行rounding，否则有可能造成调用接口失败
        rounding_price = publicparameters.rounding_price(coin)
        rounding_unit = publicparameters.rounding_unit(coin)
        # 买入时的价格
        buy_price = price_item.buy_price
        # 交易UNITS
        mk_type = coin_pair.split('_')[1]
        # 不同的基础货币有不同的买入金额
        trans_amount_per_trans = self.__regular_param.get('buy_amt').get(mk_type)
        trans_units = round(trans_amount_per_trans / buy_price, rounding_unit)
        # 第一次交易卖出时的UNIT和买入UNIT会有一个0.5%的误差
        newtrans_units = trans_units
        # 对交易价格进行ROUNDING处理
        trans_price_rounding = round(trans_price, rounding_price)
        # 有些价格较贵，金额太小出现UNIT为0的情况，不需要再提交订单
        if trans_units < 0.00001:
            return False
        # 当前交易的对象
        if trans_type == const.TRANS_TYPE_BUY:
            orderitem = cointrans.OrderItem(market, coin_pair)
        elif trans_type == const.TRANS_TYPE_SELL:
            orderitem = cointrans.OrderItem(market, coin_pair)
            # 取得当前可以卖出的总units
            account_summary = ormmysql.get_regular_invest_summary(coin_pair)
            total_units = account_summary.get('unit_balance')
            trans_units = round(total_units, rounding_unit)

        # 交易的order_market
        order_market = self.order_market

        # 提交订单
        if trans_type == const.TRANS_TYPE_SELL:
            bal = order_market.getMyBalance(coin)
            # 可能出现余额不足的情况
            if bal > trans_units:
                pass
                # trans_order=common.JSONObject({'order_id':3333})
                trans_order = order_market.submitOrder(coin_pair, trans_type, trans_price_rounding, trans_units)
            # 处理第一次买入出现扣除手续费后卖出时余额不足的情况
            elif trans_units*0.99<bal:
                newtrans_units = round(trans_units*0.99,rounding_unit)
                trans_order = order_market.submitOrder(coin_pair, trans_type, trans_price_rounding, newtrans_units)
            # 余额不足的取消卖出交易
            else:
                orderitem.sell_status = const.ORDER_STATUS_CANCEL
                # ormmysql.updateorder(orderitem)
                # ormmysql.delorder(orderitem)
                print('{0}:余额不足，已经取消订单'.format(coin))
                return False
        else:
            trans_order = order_market.submitOrder(coin_pair, trans_type, trans_price_rounding, trans_units)
        #     trans_units)
        # # 取得返回订单的信息
        order_id = trans_order.order_id
        if order_id== -1111111:
            order_status = 'fail'
            return False
        else:
            order_status = order_market.getOrderStatus(order_id, coin)
            # 如果状态为None，说明取状态有异常，对于卖出默认为OPEN，防止出现多现卖出状态设置为None，继续卖出的情况
            if order_status is None:
                order_status = const.ORDER_STATUS_OPEN
        # 保留交易时的相关信息到orderitem对象中
        if trans_type == const.TRANS_TYPE_BUY:
            orderitem.buy_order_id = order_id
            orderitem.buy_status = order_status
            orderitem.buy_price = trans_price_rounding
            orderitem.buy_amount = trans_amount_per_trans
            orderitem.buy_units = trans_units
            orderitem.buy_date = common.get_curr_time_str()
            orderitem.priceitem = price_item
            # 买入时新增加一个订单，卖出时则直接更新已经存在的订单
            # 保存数据到DB
            ormmysql.save_regular_invest(orderitem)
            # ormmysql.saveorder(orderitem)
            print('{0}:开始[{1}]交易,交易状态:{2}:PriceDate:{3},Coin:{4}, BuyPrice:{5}'.format(common.get_curr_time_str(), trans_type, order_status,
                                                               price_item.pricedate, price_item.coin,
                                                               price_item.buy_price))
        elif trans_type == const.TRANS_TYPE_SELL:
            orderitem.sell_order_id = order_id
            orderitem.sell_status = order_status
            orderitem.sell_price = trans_price_rounding
            orderitem.sell_amount = round(trans_units * trans_price_rounding, 10)
            orderitem.sell_units = trans_units
            orderitem.sell_date = common.get_curr_time_str()
            ormmysql.save_regular_invest(orderitem)
            print('{0}:开始[{1}]交易,交易状态:{2}:PriceDate:{3},Coin:{4}, BuyPrice:{5}, SellPrice:{6}, ProfiteRate:{7}'.format(common.get_curr_time_str(), trans_type, order_status,
                                                               price_item.pricedate, price_item.coin,
                                                               price_item.buy_price, orderitem.sell_price, publicparameters.SELL_PROFIT_RATE))
            # 成功卖出后把所有的买入记录清空,保存在LOG表
            # 不需要保存到LOG,明细一直保留所有的记录

            # 更新到DB
            # ormmysql.updateorder(orderitem)
            # remove to log table if sell status is closed
            # if order_status == const.ORDER_STATUS_CLOSED:
            #     ormmysql.delorder(orderitem)

        return True

if __name__ == '__main__':
    regularinvest = RegularInvest('btc38')
    regularinvest.run_regular_invest()
    # regularinvest.sell_check('ltc_btc')
    # regularinvest.regular_buy('ltc_btc')
    # regularinvest.regular_buy_indi('ltc_btc')
    # regularinvest.check_trans_indi('ltc_btc')
    # pricealert_forecast = pricealert.PriceAlert('btc38', 'ltc')
    # 当前的价格信息
    # currpriceitem = pricealert_forecast.getpriceitem('btc38', 'ltc_btc')
    # regularinvest.coin_trans('btc38','buy',currpriceitem.buy_price,currpriceitem)

    pass