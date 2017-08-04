#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'

import ordermanage,common, priceupdate, ormmysql

'''模块注释说明: 每日资金总结'''

class DailySummary(object):
    def __init__(self,market_list):
        self.__market_list=market_list

    ''' 获取当前的余额'''
    def get_balance(self):
        all_market_bal = {}
        all_coin_list = []
        for market in self.__market_list:
            order_market = ordermanage.OrderManage(market)
            market_bal = order_market.getMyBalance()
            all_market_bal[market] = market_bal
            all_coin_list = all_coin_list + list(market_bal.keys())
        # 所有市场的COIN列表
        all_coin_list = list(set(all_coin_list))
        all_coin_bal = {}
        # 当前价格的评估总价
        total_cny = 0
        # 除了open order之外的当前价格评估
        total_cny_ori = 0
        # 按币种循环生成各个市场的帐户的情况
        for coin in all_coin_list:
            all_coin_bal[coin] = []
            coinprice = pricebuff.getpriceitem(market, coin+'_cny')
            for market in self.__market_list:
                if coin in all_market_bal[market].keys():
                    coin_bal = all_market_bal[market][coin]['available']
                    coin_bal_lock = all_market_bal[market][coin]['locked']
                    coin_total_bal = round(coin_bal + coin_bal_lock, 4)
                    pricebuff = priceupdate.PriceBuffer(market, save_log_flag=False)
                    priceitem = pricebuff.getpriceitem()
                    currprice = priceitem.sell_price
                    total_est_amount = round(coin_total_bal*currprice,4)
                    # 根据自己的记录得到的balance和直接查询 得到的最终lock balance可能有差异，如果lock<open order balance则是有问题的，需要查询
                    total_open_bal = self.get_open_bal(coin)
                    # 实际价格评估的资产
                    total_cny_bal = round(coin_total_bal*currprice,4)
                    # open订单按实际买入的价格来计划金额，这个金额在每日比较会比较有用，排除价格变动造成的影响
                    total_cny_bal_with_ori_buy_amount = round((coin_total_bal-total_open_bal.get('total_unitss',0))*currprice,4)
                    # final result
                    coin_bal_item = {'date':common.get_curr_time_str(),'coin':coin, 'total_unit_bal': coin_total_bal,'est_cny':total_cny_bal, 'est_cny_ori':total_cny_bal_with_ori_buy_amount,\
                                     'availabe':coin_bal, 'locked':coin_bal_lock, 'bal_open_order':total_open_bal.get('total_units',0)
                                     }

                    all_coin_bal[coin].append({'date':common.get_curr_time_str(),'coin':coin, 'market': market, 'total': coin_total_bal, 'available':coin_bal, 'locked':coin_bal_lock})
                # else:
                #     all_coin_bal[coin].append({'date':common.get_curr_time_str(), 'market': market, 'total': 0, 'available':0, 'locked':0})
        return all_coin_bal
    '''得到OPEN订单的金额'''
    def get_open_bal(self, coin):
        # 总的挂单金额
        openlist = ormmysql.openorderlist()
        total_unit = 0
        total_amount = 0
        for openitem in openlist:
            if openitem.coin ==coin:
                total_unit = total_unit + openitem.buy_units
                total_amount = total_amount + openitem.buy_amount
        total_bal = {'total_units': total_unit, 'total_amount': total_amount}
        return total_bal

    '''输出余额到文件'''
    def output_summary(self,filename):
        file=open(filename,'a')
        #每个市场的明细
        file_detail=open(filename.split('.')[0]+'_detail.'+filename.split('.')[1],'a')
        all_market_bal={}
        all_coin_list=[]
        for market in self.__market_list:
            order_market=ordermanage.OrderManage(market)
            market_bal=order_market.getMyBalance()
            all_market_bal[market]=market_bal
            all_coin_list=all_coin_list+list(market_bal.keys())
        # 所有市场的COIN列表
        all_coin_list=list(set(all_coin_list))
        all_output={}
        all_coin_bal={}

        # 按币种循环生成各个市场的帐户的情况
        for coin in all_coin_list:
            all_coin_bal[coin]=[]
            for market in self.__market_list:
                if coin in all_market_bal[market].keys():
                    coin_bal=all_market_bal[market][coin]['available']
                    coin_bal_lock=all_market_bal[market][coin]['locked']
                    coin_total_bal = round(coin_bal + coin_bal_lock,4)
                    all_coin_bal[coin].append({'market':market,'available':coin_total_bal})
                else:
                    all_coin_bal[coin].append({'market':market,'available':0})
        # 按币种输出
        all_coin_list.sort()
        for coin in all_coin_list:
            need_output=False
            all_market_values=0
            coin_value=all_coin_bal[coin]
            for item in coin_value:
                if float(item['available'])>0:
                    need_output=True
                #市场之间的总和,针对同一币种
                all_market_values=round(all_market_values+item['available'],4)
                pass
            if need_output:
                coin_value = all_coin_bal[coin]
                for item in coin_value:
                    coin_bal=str(round(item['available'],4))
                    market=item['market']
                    all_output[market] = all_output.get(market, '') + '%s|%s|' % (coin.ljust(6), coin_bal.rjust(12))
                all_output['ALL'] = all_output.get('ALL', '') + '%s|%s|' % (coin.ljust(6), str(all_market_values).rjust(12))

        # 输出每个市场的余额
        currtime=common.CommonFunction.get_curr_time()
        for market in self.__market_list:
            output='%s|%s|%s|\n'%(currtime,market.ljust(6),all_output[market])
            file_detail.write(output)
        summary_output='%s|%s|%s|\n'%(currtime,'ALL'.ljust(6),all_output['ALL'])
        file.write(summary_output)
        file.close()
        file_detail.close()
if __name__ == '__main__':
    market_list=['bter','btc38']
    daily_summary=DailySummary(market_list)
    bal=daily_summary.output_summary('daily_summary.log',)
    pass