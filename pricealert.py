#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-8 下午11:21
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : pricealert.py
# @Software: PyCharm
# ===============================================

import sms, ordermanage, json, time, datetime
import priceupdate,common, config
import pandas as pd

'''监测价格进行预警通知'''
# 调用方法, 直接运行方法 run_price_alert()
# 使用该模块实现对价格的上升或者下降进行预警,以方便操作

class PriceAlert(object):
    def __init__(self, market_list, coin_pair_list):
        # 预警的上升和下降比例
        self.__alert_percent_up = 0.04
        self.__alert_percent_down = -0.04
        # 变化的时间范围，单位为小时
        self.__alert_duration = 1
        # 发送短信或者邮件通知的时间间隔,单位为小时
        self.__send_duration =0.5
        # 下次发送时间
        self.__last_send_time = None
        # 市场列表和COIN列表
        self.__market_list =market_list
        self.__coin_pair_list = coin_pair_list
        # price temporary file
        self.__temp_price_file_name = 'tempprice.txt'
        self.__price_file = open(self.__temp_price_file_name,'a')
        # 发送手机号
        self.__mobile = '13166366407'


        pass
    '''生成统一的警告消息内容'''
    def get_warning_message(self, chg_info):
        coin_pair = chg_info.get('coin_pair')
        chg_percent = round(chg_info.get('percent')*100,2)
        begin_price = chg_info.get('begin')
        end_price =chg_info.get('end')
        begin_depth = round(chg_info.get('depth_begin'),0)
        end_depth =  round(chg_info.get('depth_end'),0)
        message = '[{0}]:change percent [{1}%] @{2},[{3}] hour ago,Price[{4}->{5}] Buy Depth[{6}->{7}]'
        message =message.format(coin_pair, chg_percent, common.get_curr_time_str(), \
                                self.__alert_duration,begin_price,end_price, begin_depth, end_depth )
        message = message + config.sms_auth.get('signature')
        return message
        pass

    '''短时间剧烈价格变动通知,确保非常时间价格的变更不会造成重大损失'''
    def fast_chg_warning(self,coin_pair):
        # 紧急剧烈变动通知,以15分钟为一个周期
        ori_alert_duration = self.__alert_duration
        self.__alert_duration = 0.25
        fast_chg_info = self.get_change_percent(coin_pair)
        # 复原默认的周期
        fast_chg_percent = round(fast_chg_info.get('percent'), 3)
        # 15分钟内变动超过10的需要警告
        if fast_chg_percent>=0.1 or fast_chg_percent<=-0.1:
            warning_message = self.get_warning_message(fast_chg_info)
            sms.sms_send(self.__mobile, warning_message)
            # print(warning_message)
        self.__alert_duration = ori_alert_duration
        pass
    '''是否上升到预定比例'''
    def match_alert_percent(self, coin_pair):
        # chg_percent = self.get_change_percent(coin_pair)
        chg_info = self.get_change_percent(coin_pair)
        chg_percent = round(chg_info.get('percent'),3)
        # 检查快速异常的变动
        self.fast_chg_warning(coin_pair)
        # 预定时间内变化超过预期的处理
        if chg_percent>self.__alert_percent_up or chg_percent<self.__alert_percent_down:
            if self.__last_send_time is None:
                message = self.get_warning_message(chg_info)
                sms.sms_send(self.__mobile, message)
                self.__last_send_time = datetime.datetime.now()
            else:
                # 超过发送的时间间隔则清空时间，捕获下次发送时间
                if datetime.datetime.now() - self.__last_send_time > datetime.timedelta(seconds=self.__send_duration*3600):
                    self.__last_send_time = None

        pass
    '''当前的上升或者下降比例'''
    def get_change_percent(self, coin_pair):
        pdprice = pd.read_csv(self.__temp_price_file_name,',')
        # print(pdprice['price_date'])
        # 变成日期索引
        pdprice['price_date'] = pd.to_datetime(pdprice['price_date'],format='%Y-%m-%d %H:%M:%S')
        pdprice.set_index("price_date", inplace=False)
        # 过滤记录，只处理指定时间范围内的记录
        start_date = datetime.datetime.now() - datetime.timedelta(seconds=self.__alert_duration*3600)
        process_price = pdprice[(pdprice['price_date']>start_date) & (pdprice['coin_pair']==coin_pair)]
        cnt = process_price['buy_price'].count()-1

        if cnt >=0:
            # 价格信息
            last_price = process_price.iloc[cnt]['buy_price']
            first_price = process_price['buy_price'].iloc[0]
            # 价格深度
            depth_last = process_price.iloc[cnt]['buy_depth']
            depth_first = process_price['buy_depth'].iloc[0]
        else:
            # 没有记录时默认为1
            first_price = 1
            last_price =first_price
            depth_last =1
            depth_first =1
        change_percent = (last_price -first_price)/first_price
        depth_chg_percent = round((depth_last - depth_first)/depth_first,3)
        # 当前价格和指定时间 段之前的差异百分比
        change_percent = round(change_percent, 3)
        change_info = {"coin_pair":coin_pair, "begin":first_price, "end":last_price, "percent":change_percent,\
                       "depth_begin":depth_first, "depth_end":depth_last, "depth_percent":depth_chg_percent\
                       }
        return change_info
        pass
    '''取价格信息'''
    '''从市场取得价格，返回一个价格明细'''
    def getprice(self, market, coin_pair):
        try:
            order_market = ordermanage.OrderManage(market)
            price_depth = order_market.getMarketDepth(coin_pair)
            buy_depth = 0
            sell_depth = 0
            priceitem = None
            coin = coin_pair.split('_')[0]
            # use the sell price as buy_price
            buy_price = price_depth.sell[0][0]
            # use the buy orderprice as sell price
            sell_price = price_depth.buy[0][0]
            # 尝试列表中所有的买入和
            for buy_item in price_depth.buy:
                buy_depth = buy_depth + buy_item[1]
            for sell_item in price_depth.sell:
                sell_depth = sell_depth + sell_item[1]
            buy_depth = round(buy_depth, 2)
            sell_depth = round(sell_depth, 2)
            # 把价格日期保存成字符串
            priceitem = priceupdate.PriceItem(common.get_curr_time_str(), coin, buy_price, buy_depth, sell_price,
                                              sell_depth)
            # result = {"market":market, "coin_pair": coin_pair}
            result ='{0},{1},{2},{3},{4},{5},{6}\n'.format(market,coin_pair,common.get_curr_time_str(),buy_price,buy_depth,sell_price,sell_depth)
        except Exception as e:
            print('取得[{1}]价格列表时错误：{0}'.format(str(e), coin_pair))
            return None
        return result
    '''把价格加入列表'''
    def add_new_price(self, priceitem):
        self.__price_file.write(priceitem)
        self.__price_file.flush()
        pass
    '''获取一次所有市场和所有监控COIN的新价格'''
    def one_round_price(self):
        for market in self.__market_list:
            for coin_pair in self.__coin_pair_list:
                newprice = self.getprice(market, coin_pair)
                if newprice is not None:
                    self.add_new_price(newprice)

        pass
    '''循环获取价格列表'''
    def loop_new_price(self):
        run_times = 0

        while(True):
            self.one_round_price()
            df1= pd.read_csv(self.__temp_price_file_name)
            # print(df1.describe())
            time.sleep(2)
            run_times = run_times +1
            # 每运行10次检查一下是不是需要发通知
            if run_times%10 == 0:
                for coin_pair in self.__coin_pair_list:
                    self.match_alert_percent(coin_pair)
    '''分析价格趋势'''
def run_price_alert():
    coin_pair_list = config.price_monitor_coin_list.get('coinlist').split(',')
    market_list = ['btc38']
    pricealert = PriceAlert(market_list, coin_pair_list)
    pricealert.loop_new_price()



if __name__ == '__main__':

    run_price_alert()
    pricealert = PriceAlert(['btc38'],['ltc_btc'])
    pricealert.fast_chg_warning('ltc_btc')
    #
    # pricealert.loop_new_price()

    # pricealert.match_alert_percent('ltc_btc')

    pass