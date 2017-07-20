#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-18 下午10:43

import const, publicparameters, ordermanage, common
import priceupdate
'''对查找到的COIN进行交易，买入或者卖出'''

'''交易结构'''
class OrderItem(object):
    def __init__(self, coin):

        # 预测价格的信息
        self.priceitem = None
        # coin
        self.__coin = coin
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
        self.sell_unts = None
        # 卖出金额
        self.sell_amount = None
        # 卖出日期
        self.sell_date = None
        # 卖出状态
        self.sell_status = None

'''交易类'''
class CoinTrans(object):
    def __init__(self):
        # 订单状态
        const.ORDER_STATUS_OPEN = 'Open'
        const.ORDER_STATUS_CLOSED = 'Closed'
        const.TRANS_TYPE_BUY='buy'
        const.TRANS_TYPE_SELL='sell'
        # order 列表,所有交易的列表保存在这个列表中
        self.order_list = []
        # 最大的交易订单数，
        self.__max_open_order_pool = publicparameters.MAX_OPEN_ORDER_POOL
        # 每次交易的金额
        self.__trans_amount_per_trans = publicparameters.TRANS_AMOUNT_PER_ORDER
        # 止盈比例
        self.__sell_profit_rate = publicparameters.SELL_PROFIT_RATE

        pass

    '''查询已经存在的orderitem, 并返回'''
    def get_order_item(self, priceitem):
        orderitem_result = None
        for item in self.order_list:
            if item.priceitem.pricedate == priceitem.pricedate and item.priceitem.coin == priceitem.coin\
                and item.priceitem.buy_price == priceitem.buy_price:
                orderitem_result = item
                break
        return orderitem_result

    '''更新订单列表中状态'''
    # TODO 更新
    def update_order_status(self):
        pass
    def test_coin_trans(self):
        pricebuffer = priceupdate.PriceBuffer(save_log_flag=False)
        priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
        orderstatus1 = self.coin_trans('btc38', 'buy', 0.006, priceitem)
        orderstatus2 = self.coin_trans('btc38', 'sell', 0.02, priceitem)
        print('order status 1: {0}, 2: {1}'.format(orderstatus1, orderstatus2))

    '''交易信息
    @market ==btc38, bter
    @trans_type   =='sell', 'buy'
    @trans_price    交易价格
    @price_item     预测价格时的信息，用来进行对比
    '''

    def coin_trans(self, market, trans_type, trans_price, price_item):
        coin = price_item.coin
        coin_pair = coin+'_cny'
        # 对价格和交易单位进行rounding，否则有可能造成调用接口失败
        rounding_price = publicparameters.rounding_price(coin)
        rounding_unit = publicparameters.rounding_unit(coin)
        # 买入时的价格
        buy_price = price_item.buy_price
        # 交易UNITS
        trans_units = round(self.__trans_amount_per_trans / buy_price, rounding_unit)
        # 对交易价格进行ROUNDING处理
        trans_price_rounding = round(trans_price, rounding_price)
        # 当前交易的对象
        if trans_type == const.TRANS_TYPE_BUY:
            orderitem = OrderItem(coin)
        elif trans_type == const.TRANS_TYPE_SELL:
            # 卖出时查找已经存在的priceitem，并更新相应的状态
            orderitem = self.get_order_item(price_item)
            # 卖出订单时检查买入订单的状态，如果没有买入成功则停止卖出，返回失败
            if orderitem.buy_status != const.ORDER_STATUS_CLOSED:
                return False
        # 交易的order_market
        order_market = ordermanage.OrderManage(market)

        # 提交订单
        trans_order = order_market.submitOrder(coin_pair, trans_type, trans_price_rounding,\
            trans_units)
        # 取得返回订单的信息
        order_id = trans_order.order_id
        order_status = order_market.getOrderStatus(order_id, coin)
        # 保留交易时的相关信息到orderitem对象中
        if trans_type == const.TRANS_TYPE_BUY:
            orderitem.buy_order_id = order_id
            orderitem.buy_status = order_status
            orderitem.buy_price = trans_price_rounding
            orderitem.buy_amount = self.__trans_amount_per_trans
            orderitem.buy_units = trans_units
            orderitem.buy_date = common.get_curr_time_str()
            orderitem.priceitem = price_item
            # 买入时新增加一个订单，卖出时则直接更新已经存在的订单
            self.order_list.append(orderitem)

        elif trans_type == const.TRANS_TYPE_SELL:
            orderitem.sell_order_id = order_id
            orderitem.sell_status = order_status
            orderitem.sell_price = trans_price_rounding
            orderitem.sell_amount = round(trans_units * trans_price_rounding, 2)
            orderitem.sell_unts = trans_units
            orderitem.sell_date = common.get_curr_time_str()

        return True
        pass




if __name__ == '__main__':
    trans = CoinTrans()
    trans.test_coin_trans()
    pass