#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-18 下午10:43

import shelve
import const, publicparameters, ordermanage, common
import priceupdate
'''对查找到的COIN进行交易，买入或者卖出'''

'''交易结构'''
class OrderItem(object):
    def __init__(self, market, coin):

        # 预测价格的信息
        self.priceitem = None
        # market
        self.market = market
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
    '''转换成字符保存'''
    # TODO
    def __repr__(self):
        order_detail_format = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}|{10}'
        if self.sell_amount is not None:
            profit_amount = self.sell_amount - self.buy_amount
        else:
            profit_amount = ''
        return order_detail_format.format(self.market,self.__coin, profit_amount, self.buy_order_id,self.buy_date,self.buy_status,self.buy_price,\
                                          self.buy_amount,self.buy_units,self.sell_order_id,self.sell_date,self.sell_status,self.sell_amount,self.sell_unts)
    # 打印出来字符
    def __str__(self):
        return self.__repr__()

'''交易类'''
class CoinTrans(object):
    def __init__(self, market):
        # 订单状态
        const.ORDER_STATUS_OPEN = 'open'
        const.ORDER_STATUS_CLOSED = 'closed'
        const.TRANS_TYPE_BUY='buy'
        const.TRANS_TYPE_SELL='sell'
        # order 列表,所有交易的列表保存在这个列表中,交易列表是个公共列表，以方便统一处理
        self.order_list = publicparameters.ORDER_LIST
        # 最大的交易订单数，
        self.__max_open_order_pool = publicparameters.MAX_OPEN_ORDER_POOL
        # 每次交易的金额
        self.__trans_amount_per_trans = publicparameters.TRANS_AMOUNT_PER_ORDER
        # 止盈比例
        self.__sell_profit_rate = publicparameters.SELL_PROFIT_RATE
        # 市场的交易处理器
        self.order_market = ordermanage.OrderManage(market)

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
    def update_order_status(self):
        for orderitem in self.order_list:
            if orderitem.buy_status == const.ORDER_STATUS_OPEN:
                order_status = self.order_market.getOrderStatus(orderitem.buy_order_id, orderitem.priceitem.coin)
                orderitem.buy_status = order_status
            if orderitem.sell_status == const.ORDER_STATUS_OPEN:
                order_status = self.order_market.getOrderStatus(orderitem.buy_order_id, orderitem.priceitem.coin)
                orderitem.sell_status = order_status
        # 把更新的结果保存到文件中
        self.save_order()
        # 更新状态完成后，把最新的结果保存起来
        pass
    '''保存订单到不同的文件中以便查询'''
    def save_order(self):
        # OPEN状态的，每次都是替换保存，放最新的数据在里面
        # open_trans_file = open('open_trans.log','w')
        open_trans_file = shelve.open('open_trans.dat')
        # 把格式化的内容保存到log表中，和上面的数据是一致的，只是显示更加容易
        open_trans_log = open('open_trans.log','w')
        # 清除已经存在 的内容
        open_trans_file.clear()
        # 把当前OPEN交易信息保存起来
        orderindex = 0
        for orderitem in self.order_list:
            if orderitem.buy_status == const.ORDER_STATUS_OPEN or orderitem.sell_status == const.ORDER_STATUS_OPEN:
                # 按对象保存，容易加载
                open_trans_file[orderindex] = orderitem
                # 格式化保存，供运行时参考
                open_trans_log.write(str(orderitem))
        open_trans_file.close()

    # 判断是不是满足买入或者卖出条件
    def check_trans_indi(self):
        # 总共的OPEN交易订单
        total_open_count = self.get_open_order_count()
        if total_open_count > publicparameters.MAX_OPEN_ORDER_POOL:
            return False

        return True
        pass

    # 目前交易列表中OPEN的交易数量
    def get_open_order_count(self):
        # 只有买入和卖出都成功的才算是结束的交易
        total_open_order = 0
        for orderitem in self.order_list:
            if orderitem.buy_status == const.ORDER_STATUS_OPEN or orderitem.sell_status == const.ORDER_STATUS_OPEN:
                total_open_order = total_open_order + 1
        return total_open_order
        pass

    # 交易测试
    def test_coin_trans(self):
        pricebuffer = priceupdate.PriceBuffer(save_log_flag=False)
        priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
        orderstatus1 = self.coin_trans( 'btc38', 'buy', 0.006, priceitem)
        orderstatus2 = self.coin_trans( 'btc38', 'sell', 0.02, priceitem)
        print('order status 1: {0}, 2: {1}'.format(orderstatus1, orderstatus2))
        # 更新订单的状态
        self.update_order_status()

    '''交易信息
    @market ==btc38, bter
    @trans_type   =='sell', 'buy'
    @trans_price    交易价格
    @price_item     预测价格时的信息，用来进行对比
    '''
    def coin_trans(self, market, trans_type, trans_price, price_item):
        # 判断是不是满足交易的条件，不满足则退出不进行交易
        if self.check_trans_indi() is False:
            return False

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
            orderitem = OrderItem(market, coin)
        elif trans_type == const.TRANS_TYPE_SELL:
            # 卖出时查找已经存在的priceitem，并更新相应的状态
            orderitem = self.get_order_item(price_item)
            # 卖出订单时检查买入订单的状态，如果没有买入成功则停止卖出，返回失败
            if orderitem.buy_status != const.ORDER_STATUS_CLOSED:
                return False
        # 交易的order_market
        order_market = self.order_market

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
    trans = CoinTrans('btc38')
    trans.test_coin_trans()
    print(len(publicparameters.ORDER_LIST))
    pass