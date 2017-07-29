#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-18 下午10:43

import shelve
import const, publicparameters, ordermanage, common
import priceupdate, ormmysql
import time
'''对查找到的COIN进行交易，买入或者卖出'''

'''交易结构'''
class OrderItem(object):
    def __init__(self, market, coin):

        # 预测价格的信息
        self.priceitem = None
        # market
        self.market = market
        # coin
        self.coin = coin
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
        self.sell_units = None
        # 卖出金额
        self.sell_amount = None
        # 卖出日期
        self.sell_date = None
        # 卖出状态
        self.sell_status = None
    '''生成表的动态类，用来自动生成ORM的模型'''
    def gen_table_class(self):

        create_table_sql = 'CREATE TABLE IF NOT EXISTS t_coin_trans (\n'+\
                    'trans_id INT(11) NOT NULL AUTO_INCREMENT,\n'
        table_class= 'orderitemTable = Table(\n'+ '"t_coin_trans", metadata,\n'+ \
                     "Column('trans_id', INT(11), primary_key=True),\n"
        for name, value in vars(self).items():
            # Column('trans_id', Integer, primary_key=True),
            table_class = table_class + "Column('{0}', VARCHAR(100)),\n".format(name)
            create_table_sql = create_table_sql + "'{0}' VARCHAR(100),\n".format(name)
        create_table_sql = create_table_sql[:len(create_table_sql)-2]+'\n)'
        table_class = table_class[:len(table_class)-2] +'\n)'
        print(table_class)
        print(create_table_sql)
        return table_class
    '''转换成字符保存'''
    # TODO
    def __repr__(self):
        order_detail_format = '{0}|{1}|{2}|{3}|{4}|{5}|{6}|{7}|{8}|{9}|{10}|{11}|{12}|{13}|\n'
        if self.sell_amount is not None:
            profit_amount = round(self.sell_amount - self.buy_amount,2)
        else:
            profit_amount = ''
        return order_detail_format.format(self.market.rjust(8),self.coin.rjust(6), profit_amount, self.buy_order_id,self.buy_date,\
                                          self.buy_status,self.buy_price,self.buy_amount,self.buy_units,self.sell_order_id,\
                                          self.sell_date,self.sell_status,self.sell_amount,self.sell_units)
    # 打印出来字符
    def __str__(self):
        return self.__repr__()

'''交易类'''
class CoinTrans(object):
    def __init__(self, market):
        # 订单状态
        const.ORDER_STATUS_OPEN = 'open'
        const.ORDER_STATUS_CLOSED = 'closed'
        const.ORDER_STATUS_CANCEL = 'cancelled'
        const.TRANS_TYPE_BUY='buy'
        const.TRANS_TYPE_SELL='sell'

        # 最大的交易订单数，
        self.__max_open_order_pool = publicparameters.MAX_OPEN_ORDER_POOL
        # 每次交易的金额
        self.__trans_amount_per_trans = publicparameters.TRANS_AMOUNT_PER_ORDER
        # 止盈比例
        self.__sell_profit_rate = publicparameters.SELL_PROFIT_RATE
        # 市场的交易处理器
        self.order_market = ordermanage.OrderManage(market)
        # 市场
        self.market = market

        pass
    '''卖出条件检查'''
    def sell_check(self):
        open_order_list = ormmysql.openorderlist()
        for curroderitem in open_order_list:
            # The transaction of selling is in progress then check next
            if curroderitem.sell_status ==const.ORDER_STATUS_OPEN:
                continue
            pricebuffer = priceupdate.PriceBuffer(self.market, save_log_flag=False)
            # 获取当前的价格

            newpriceitem = pricebuffer.getpriceitem(self.market, curroderitem.coin+'_cny')
            if newpriceitem is not None and curroderitem.buy_status == const.ORDER_STATUS_CLOSED:
                # 测试，卖单提前生成好，等待直接成效
                rounding_num = publicparameters.rounding_unit(curroderitem.coin)
                default_sell_price = round(curroderitem.buy_price*(1+publicparameters.SELL_PROFIT_RATE),rounding_num)
                trans_status = self.coin_trans(self.market, 'sell', default_sell_price, curroderitem.priceitem)
                # if newpriceitem.buy_price >= curroderitem.buy_price*(1+publicparameters.SELL_PROFIT_RATE):
                #     # 执行实际的卖出操作
                #     trans_status = self.coin_trans(self.market, 'sell', newpriceitem.buy_price, curroderitem.priceitem)
                #
                #     if trans_status is True:
                #         pass
                        # print('{0}:已经成功卖出,价格:{1}, coin: {2}, 盈利百分比: {3}'.format(common.get_curr_time_str(), newpriceitem.buy_price,\
                        #                                                         curroderitem.coin, publicparameters.SELL_PROFIT_RATE))

    '''查询已经存在的orderitem, 并返回'''
    def get_order_item(self, priceitem):
        orderitem_result = None
        order_list = ormmysql.openorderlist()
        for item in order_list:
            if item.priceitem.pricedate == priceitem.pricedate and item.priceitem.coin == priceitem.coin\
                and item.priceitem.buy_price == priceitem.buy_price:
                orderitem_result = item
                break
        return orderitem_result

    '''更新订单列表中状态'''
    def update_order_status(self):
        order_list = ormmysql.openorderlist()
        for orderitem in order_list:
            if orderitem.buy_status == const.ORDER_STATUS_OPEN:
                order_status = self.order_market.getOrderStatus(orderitem.buy_order_id, orderitem.priceitem.coin)
                orderitem.buy_status = order_status
                ormmysql.updateorder(orderitem)
            if orderitem.sell_status == const.ORDER_STATUS_OPEN:
                order_status = self.order_market.getOrderStatus(orderitem.sell_order_id, orderitem.priceitem.coin)
                orderitem.sell_status = order_status
                ormmysql.updateorder(orderitem)
                if order_status == const.ORDER_STATUS_CLOSED:
                    # 把交易记录从交易表转移到LOG表
                    ormmysql.delorder(orderitem)
                    profit_amount = round(orderitem.sell_amount - orderitem.buy_amount,3)
                    print('{0}:[{1}]{smile}已经成功交易,盈利{2}！ BuyPrice:{3}, SellPrice:{4}, ProfiteRate:{5}'.format(\
                            common.get_curr_time_str(), orderitem.priceitem.coin, profit_amount, orderitem.buy_price, orderitem.sell_price,\
                            publicparameters.SELL_PROFIT_RATE, smile='^_^ '*5))

                    # the sell status is closed to move log table
            # 这里会导致出问题，出现上面更新后又再次删除的情况
            # if orderitem.sell_status == const.ORDER_STATUS_CLOSED:
            #     # 把交易记录从交易表转移到LOG表
            #     ormmysql.delorder(orderitem)
        pass

    '''取消超时买入订单，买入挂单超过指定的时间则取消'''
    # TODO 这个功能还需要完善
    def cancle_ot_buy_order(self, duration):
        open_order_list = ormmysql.openorderlist()
        curr_time = common.CommonFunction.get_curr_date()
        for curr_order_item in open_order_list:
            diff = curr_time - common.CommonFunction.strtotime(curr_order_item.buy_date)
            diffseconds = diff.seconds
            # Only cancel the buy status =open
            if diffseconds >duration and curr_order_item.buy_status == const.ORDER_STATUS_OPEN:
                cancel_status = self.order_market.cancelOrder(curr_order_item.buy_order_id, curr_order_item.coin)
                if cancel_status == 'success':
                    curr_order_item.buy_status=const.ORDER_STATUS_CANCEL
                    # update the buy status
                    ormmysql.updateorder(curr_order_item)
                    # move the records to log table
                    ormmysql.delorder(curr_order_item)
                    pass

    # '''保存订单到数据库文件中以便查询'''
    # def save_order(self, orderitem, ordertype = 'new'):
    #     # 保存新的和更新的订单到文件中
    #     open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
    #     ordernum = len(open_trans_file_db.items()) + 1
    #     ordername = 'order{0}'.format(ordernum)
    #     if ordertype == 'new':
    #         # 直接增加一条记录
    #         open_trans_file_db[ordername] = orderitem
    #     #     查找到对应的记录并更新
    #     elif ordertype == 'update':
    #         for order in open_trans_file_db.items():
    #             curritem = order[1]
    #             if curritem.coin == orderitem.coin and curritem.buy_date == orderitem.buy_date:
    #                 open_trans_file_db[order[0]] = orderitem
    #                 break
    #     open_trans_file_db.close()
    #
    #     pass
    #

    # 判断是不是满足买入或者卖出条件
    def check_trans_indi(self, coin=None):
        # 总共的OPEN交易订单
        total_open_count = ormmysql.openordercount()
        if total_open_count >= publicparameters.MAX_OPEN_ORDER_POOL:
            return False
        if coin is not None:
            coin_rate = self.get_coin_rate_in_open_orders(coin)
            # 大于单个COIN在总的OPEN数量中允许的最大比例
            if coin_rate > publicparameters.COIN_MAX_RATE_IN_OPEN_ORDERS:
                return False
        return True
        pass
    # coin percentage out of total allow open orders,
    def get_coin_rate_in_open_orders(self, coin):
        open_order_list = ormmysql.openorderlist()
        # total_count = ormmysql.openordercount()
        # 用POOL的最大值来检查单个币种的比例
        total_count = publicparameters.MAX_OPEN_ORDER_POOL
        coin_count = 0
        for open_order in open_order_list:
            if open_order.coin == coin:
                coin_count = coin_count + 1
        if total_count == 0:
            rate =0
        else:
            rate = round(coin_count/total_count,2)
        return rate

    # 交易测试
    def test_coin_trans(self):
        pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
        priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
        # 循环检查OPEN订单是不是满足卖出条件

        orderstatus1 = self.coin_trans( 'btc38', 'buy', 0.01224, priceitem)
        # orderstatus2 = self.coin_trans( 'btc38', 'sell', 0.01345, priceitem)
        # print('order status 1: {0}, 2: {1}'.format(orderstatus1, orderstatus2))
        runtimes = 0
        while (True):
            self.update_order_status()
            pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
            newpriceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
            order_list = ormmysql.openorderlist()
            for openorderitem in order_list:
                if openorderitem.buy_status == const.ORDER_STATUS_CLOSED:
                    # 满足卖出条件后提交卖出订单
                    if newpriceitem.buy_price>openorderitem.buy_price*(1+self.__sell_profit_rate) and openorderitem.sell_status ==const.ORDER_STATUS_OPEN:
                        self.coin_trans('btc38', 'sell', newpriceitem.buy_price, openorderitem.priceitem)
                        print('满足卖出条件，提交了定单{0}, 卖出价格:{1}'.format(openorderitem.sell_order_id, newpriceitem.buy_price))
            runtimes = runtimes + 1
            time.sleep(5)
            print('has run %d times'%runtimes)
            pass

        # 更新订单的状态
        self.update_order_status()

    '''交易信息
    @market ==btc38, bter
    @trans_type   =='sell', 'buy'
    @trans_price    交易价格
    @price_item     预测价格时的信息，用来进行对比
    '''
    def coin_trans(self, market, trans_type, trans_price, price_item):
        coin = price_item.coin
        coin_pair = coin+'_cny'

        # 判断是不是满足交易的条件，不满足则退出不进行交易
        if trans_type == const.TRANS_TYPE_BUY:
            if self.check_trans_indi(coin) is False:
                print('{0}:不符合买入条件，可能是超过买入数量上限或者比例上限'.format(coin))
                return False

        # 对价格和交易单位进行rounding，否则有可能造成调用接口失败
        rounding_price = publicparameters.rounding_price(coin)
        rounding_unit = publicparameters.rounding_unit(coin)
        # 买入时的价格
        buy_price = price_item.buy_price
        # 交易UNITS
        trans_units = round(self.__trans_amount_per_trans / buy_price, rounding_unit)
        # 对交易价格进行ROUNDING处理
        trans_price_rounding = round(trans_price, rounding_price)
        # 有些价格较贵，金额太小出现UNIT为0的情况，不需要再提交订单
        if trans_units < 0.00001:
            return False
        # 当前交易的对象
        if trans_type == const.TRANS_TYPE_BUY:
            orderitem = OrderItem(market, coin)
        elif trans_type == const.TRANS_TYPE_SELL:
            # 卖出时查找已经存在的priceitem，并更新相应的状态
            orderitem = self.get_order_item(price_item)
            if orderitem is None:
                return False
            else:
                trans_units = orderitem.buy_units
            # 卖出订单时检查买入订单的状态，如果没有买入成功则停止卖出，返回失败
            if orderitem.buy_status != const.ORDER_STATUS_CLOSED:
                # print('买入订单还没有成交，卖出取消!')
                return False
        # 交易的order_market
        order_market = self.order_market

        # 提交订单
        if trans_type == const.TRANS_TYPE_SELL:
            bal = order_market.getMyBalance(coin)
            # 可能出现余额不足的情况
            if bal > trans_units:
                trans_order = order_market.submitOrder(coin_pair, trans_type, trans_price_rounding, trans_units)
            # 余额不足的取消卖出交易
            else:
                orderitem.sell_status = const.ORDER_STATUS_CANCEL
                ormmysql.updateorder(orderitem)
                ormmysql.delorder(orderitem)
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
            # 保存数据到DB
            ormmysql.saveorder(orderitem)
            print('{0}:开始[{1}]交易,交易状态:{2}:PriceDate:{3},Coin:{4}, BuyPrice:{5}'.format(common.get_curr_time_str(), trans_type, order_status,
                                                               price_item.pricedate, price_item.coin,
                                                               price_item.buy_price))
        elif trans_type == const.TRANS_TYPE_SELL:
            orderitem.sell_order_id = order_id
            orderitem.sell_status = order_status
            orderitem.sell_price = trans_price_rounding
            orderitem.sell_amount = round(trans_units * trans_price_rounding, 2)
            orderitem.sell_units = trans_units
            orderitem.sell_date = common.get_curr_time_str()
            print('{0}:开始[{1}]交易,交易状态:{2}:PriceDate:{3},Coin:{4}, BuyPrice:{5}, SellPrice:{6}, ProfiteRate:{7}'.format(common.get_curr_time_str(), trans_type, order_status,
                                                               price_item.pricedate, price_item.coin,
                                                               price_item.buy_price, orderitem.sell_price, publicparameters.SELL_PROFIT_RATE))
            # 更新到DB
            ormmysql.updateorder(orderitem)
            # remove to log table if sell status is closed
            if order_status == const.ORDER_STATUS_CLOSED:
                ormmysql.delorder(orderitem)

        return True
        pass




if __name__ == '__main__':
    #
    # orderitem = OrderItem('btc38', 'doge')
    # orderitem.gen_table_class()
    #
    #
    trans = CoinTrans('btc38')
    # trans.test_coin_trans()
    #
    #
    pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
    priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')

    trans.cancle_ot_buy_order(10)
    #
    # trans.cancle_ot_buy_order(50)
    # trans.sell_check()
    # # time.sleep(2)
    # priceitem2 = pricebuffer.getpriceitem('btc38', 'doge_cny')
    #
    # # 循环检查OPEN订单是不是满足卖出条件
    #
    # orderstatus1 = trans.coin_trans( 'btc38', 'buy', 0.009, priceitem)
    trans.sell_check()
    # trans.update_order_status()

    # orderstatus2 = trans2.coin_trans( 'btc38', 'buy', 0.009, priceitem2)
    # print(len(publicparameters.ORDER_LIST))
    # print(len(trans2.order_list))


    # orderstatus2 = trans.coin_trans( 'btc38', 'sell', 0.01345, priceitem)
    # print('order status 1: {0}, 2: {1}'.format(orderstatus1, orderstatus2))


    # print(len(publicparameters.ORDER_LIST))
    pass