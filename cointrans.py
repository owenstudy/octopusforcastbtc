#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-18 下午10:43

import shelve
import const, publicparameters, ordermanage, common
import priceupdate
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
        const.TRANS_TYPE_BUY='buy'
        const.TRANS_TYPE_SELL='sell'

        # 临时保存的文件名称
        self.open_trans_file_log_name = publicparameters.OPEN_TRANS_FILE+'.log'
        # 保存在sheleve中以方便加载
        self.open_trans_file_db_name = publicparameters.OPEN_TRANS_FILE+'.dat'
        self.closed_trans_file_db_name = publicparameters.CLOSED_TRANS_FILE+ '.dat'
        self.closed_trans_file_log_name= publicparameters.CLOSED_TRANS_FILE+ '.log'
        # 三个文件处理器
        # self.open_trans_file_db = shelve.open(self.open_trans_file_db_name)
        # self.open_trans_file_log = open(self.open_trans_file_log_name,'w')
        # self.close_trans_file_db = shelve.open(self.closed_trans_file_db_name)

        # 加载最后一次程序运行停止后的数据
        self.__load_last_trans()

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
        # 市场
        self.market = market

        pass
    '''加载上次未处理完成的trans'''
    def __load_last_trans(self):
        # 只有程序刚运行时并且文件中有数据时才加载
        # if len(publicparameters.ORDER_LIST) != 0:
        #     return
        # 从文件中加载上次运行时的订单数据
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)

        last_order_list = []
        # if len(last_open_trans.items()) == 0:
        #     last_order_list = []
        # else:
        for item in open_trans_file_db.items():
            orderitem = open_trans_file_db[item[0]]
            last_order_list.append(orderitem)

        publicparameters.ORDER_LIST = last_order_list
        self.order_list = last_order_list

        open_trans_file_db.close()

    '''卖出条件检查'''
    def sell_check(self):
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
        for curritem in open_trans_file_db.items():
            ordername = curritem[0]
            curroderitem = curritem[1]
            pricebuffer = priceupdate.PriceBuffer(self.market, save_log_flag=False)
            # 获取当前的价格
            newpriceitem = pricebuffer.getpriceitem(self.market, curroderitem.coin+'_cny')
            if newpriceitem is not None and curroderitem.buy_status == const.ORDER_STATUS_CLOSED:
                if newpriceitem.buy_price >= curroderitem.buy_price*(1+publicparameters.SELL_PROFIT_RATE):
                    # 执行实际的卖出操作
                    trans_status = self.coin_trans(self.market, 'sell', newpriceitem.buy_price, curroderitem.priceitem)
                    if trans_status is True:
                        print('{0}:已经成功卖出,价格:{1}, coin: {2}, 盈利百分比: {3}'.format(common.get_curr_time_str(), newpriceitem.buy_price,\
                                                                                curroderitem.coin, publicparameters.SELL_PROFIT_RATE))

    '''查询已经存在的orderitem, 并返回'''
    def get_order_item(self, priceitem):
        orderitem_result = None
        for item in self.order_list:
            if item.priceitem.pricedate == priceitem.pricedate and item.priceitem.coin == priceitem.coin\
                and item.priceitem.buy_price == priceitem.buy_price:
                orderitem_result = item
                break
        return orderitem_result
    '''OPEN列表中的ORDER已经成功结束，则从OPEN列表中删除，并加入到close列表'''
    def remove_closed_order(self, orderitem):
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
        closed_trans_file_db = shelve.open(self.closed_trans_file_db_name, writeback=True)
        for curritem in open_trans_file_db.items():
            ordername = curritem[0]
            curroderitem = curritem[1]
            if curroderitem.coin == orderitem.coin and curroderitem.buy_date == orderitem.buy_date:
                # 保存到close file中
                closed_trans_file_db[ordername] = orderitem
                # 同时从OPEN列表中删除
                del open_trans_file_db[ordername]

        open_trans_file_db.close()
        closed_trans_file_db.close()

    '''更新订单列表中状态'''
    def update_order_status(self):
        closed_order_list =[]
        for orderitem in self.order_list:
            if orderitem.buy_status == const.ORDER_STATUS_OPEN:
                order_status = self.order_market.getOrderStatus(orderitem.buy_order_id, orderitem.priceitem.coin)
                orderitem.buy_status = order_status
                self.save_order(orderitem, 'update')
            if orderitem.sell_status == const.ORDER_STATUS_OPEN:
                order_status = self.order_market.getOrderStatus(orderitem.buy_order_id, orderitem.priceitem.coin)
                orderitem.sell_status = order_status
                self.save_order(orderitem, 'update')
                # 从OPEN文件中删除并加入到CLOSE文件中
                if order_status == const.ORDER_STATUS_CLOSED:
                    self.remove_closed_order(orderitem)
                    # 加入到删除列表
                    closed_order_list.append(orderitem)
            # 检查数据，有关闭的加入到删除列表
            if orderitem.sell_status == const.ORDER_STATUS_CLOSED:
                # 加入到删除列表
                closed_order_list.append(orderitem)
                self.remove_closed_order(orderitem)

        # 从列表中删除
        for item in closed_order_list:
            try:
                self.order_list.remove(item)
            except:
                pass

        # 把OPEN记录保存LOG文件中不方便查看
        self.save_open_to_log()
        self.save_close_to_log()
        pass
    '''open记录到log文件'''
    def save_open_to_log(self):
        # 把OPEN记录保存LOG文件中不方便查看
        open_trans_file_log = open(self.open_trans_file_log_name, 'w')
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
        for item in open_trans_file_db.items():
            orderitemstr = str(item[1])
            open_trans_file_log.write(orderitemstr)
        open_trans_file_log.close()
        open_trans_file_db.close()
    '''保存close DB to log'''
    def save_close_to_log(self):
        # 把OPEN记录保存LOG文件中不方便查看
        close_trans_file_log = open(self.closed_trans_file_log_name, 'w')
        close_trans_file_db = shelve.open(self.closed_trans_file_db_name, writeback=True)
        for item in close_trans_file_db.items():
            orderitemstr = str(item[1])
            close_trans_file_log.write(orderitemstr)
        close_trans_file_db.close()
        close_trans_file_log.close()

    '''取消超时买入订单，买入挂单超过指定的时间则取消'''
    # TODO 这个功能还需要完善
    def cancle_ot_buy_order(self, duration):
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
        curr_time = common.CommonFunction.get_curr_time()
        cancel_list = []
        for item in open_trans_file_db.items():
            curr_order_item = item[1]
            diff = curr_time - curr_order_item.buy_date
            if diff >duration:
                cancel_status = self.order_market.cancelOrder(curr_order_item.buy_order_id, curr_order_item.coin)
                if cancel_status == 'success':
                    # 移除已经取消的订单
                    cancel_list.append(curr_order_item[0])
                    pass
        for cancel_item in cancel_list:

            del open_trans_file_db[cancel_item]

    '''保存订单到数据库文件中以便查询'''
    def save_order(self, orderitem, ordertype = 'new'):
        # 保存新的和更新的订单到文件中
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
        ordernum = len(open_trans_file_db.items()) + 1
        ordername = 'order{0}'.format(ordernum)
        if ordertype == 'new':
            # 直接增加一条记录
            open_trans_file_db[ordername] = orderitem
        #     查找到对应的记录并更新
        elif ordertype == 'update':
            for order in open_trans_file_db.items():
                curritem = order[1]
                if curritem.coin == orderitem.coin and curritem.buy_date == orderitem.buy_date:
                    open_trans_file_db[order[0]] = orderitem
                    break
        open_trans_file_db.close()

        pass


    # 判断是不是满足买入或者卖出条件
    def check_trans_indi(self):
        # 总共的OPEN交易订单
        total_open_count = self.get_open_order_count()
        if total_open_count >= publicparameters.MAX_OPEN_ORDER_POOL:
            return False

        return True
        pass

    # 目前交易列表中OPEN的交易数量
    def get_open_order_count(self):
        open_trans_file_db = shelve.open(self.open_trans_file_db_name, writeback=True)
        total_open_order = 0

        for item in open_trans_file_db.items():
            orderitem = item[1]
            if orderitem.buy_status == const.ORDER_STATUS_OPEN or (
                    orderitem.sell_status == const.ORDER_STATUS_OPEN or orderitem.sell_status is None):
                total_open_order = total_open_order + 1
        open_trans_file_db.close()
        return total_open_order
    def get_open_order_countX(self):
        # 只有买入和卖出都成功的才算是结束的交易
        total_open_order = 0
        for orderitem in self.order_list:
            if orderitem.buy_status == const.ORDER_STATUS_OPEN or (orderitem.sell_status == const.ORDER_STATUS_OPEN or orderitem.sell_status is None):
                total_open_order = total_open_order + 1
        return total_open_order
        pass

    # 交易测试
    def test_coin_trans(self):
        pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
        priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
        # 循环检查OPEN订单是不是满足卖出条件

        orderstatus1 = self.coin_trans( 'btc38', 'buy', 0.008, priceitem)
        # orderstatus2 = self.coin_trans( 'btc38', 'sell', 0.01345, priceitem)
        # print('order status 1: {0}, 2: {1}'.format(orderstatus1, orderstatus2))
        runtimes = 0
        while (True):
            self.update_order_status()
            pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
            newpriceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
            for openorderitem in self.order_list:
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
        # 判断是不是满足交易的条件，不满足则退出不进行交易
        if trans_type == const.TRANS_TYPE_BUY:
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
        # 有些价格较贵，金额太小出现UNIT为0的情况，不需要再提交订单
        if trans_units < 0.00001:
            return False
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
        trans_order = order_market.submitOrder(coin_pair, trans_type, trans_price_rounding, \
                                               trans_units)

        # trans_order = self.simu_submit_order (coin_pair, trans_type, trans_price_rounding,\
        #     trans_units)
        # # 取得返回订单的信息
        order_id = trans_order.order_id
        if order_id== -1111111:
            order_status = 'fail'
            return False
        else:
            order_status = order_market.getOrderStatus(order_id, coin)
        print('开始{0}交易,交易状态:{1}:{2},{3}, {4}'.format(trans_type, order_status, price_item.pricedate, price_item.coin, price_item.buy_price))

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
            # 保存最新的订单到文件中
            self.save_order(orderitem, 'new')
            self.update_order_status()

        elif trans_type == const.TRANS_TYPE_SELL:
            orderitem.sell_order_id = order_id
            orderitem.sell_status = order_status
            orderitem.sell_price = trans_price_rounding
            orderitem.sell_amount = round(trans_units * trans_price_rounding, 2)
            orderitem.sell_units = trans_units
            orderitem.sell_date = common.get_curr_time_str()
            # 保存最新的订单到文件中
            self.save_order(orderitem, 'update')
            self.update_order_status()

        return True
        pass




if __name__ == '__main__':
    trans = CoinTrans('btc38')
    # trans.test_coin_trans()

    pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
    priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')

    trans.cancle_ot_buy_order(50)
    trans.sell_check()
    # time.sleep(2)
    # priceitem2 = pricebuffer.getpriceitem('btc38', 'doge_cny')
    #
    # # 循环检查OPEN订单是不是满足卖出条件
    #
    # orderstatus1 = trans.coin_trans( 'btc38', 'buy', 0.010, priceitem)
    # trans.update_order_status()

    # orderstatus2 = trans2.coin_trans( 'btc38', 'buy', 0.009, priceitem2)
    # print(len(publicparameters.ORDER_LIST))
    # print(len(trans2.order_list))


    # orderstatus2 = trans.coin_trans( 'btc38', 'sell', 0.01345, priceitem)
    # print('order status 1: {0}, 2: {1}'.format(orderstatus1, orderstatus2))


    # print(len(publicparameters.ORDER_LIST))
    pass