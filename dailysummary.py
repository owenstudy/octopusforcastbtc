#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'

import time, json
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
        total_est_cny = 0
        # 除了open order之外的当前价格评估
        total_est_cny_ori = 0
        # 总的open order buy amount
        total_open_buy_amt = 0
        # 总的open order 估算amount
        total_open_est_cny = 0
        # 所有COIN的明细余额
        open_bal_list = []
        currdate = common.get_curr_time_str()
        # 按币种循环生成各个市场的帐户的情况
        for coin in all_coin_list:
            # time.sleep(0.5)
            for market in self.__market_list:
                if coin in all_market_bal[market].keys():
                    coin_bal = all_market_bal[market][coin]['available']
                    coin_bal_lock = all_market_bal[market][coin]['locked']
                    if coin == 'cny':
                        total_cny_bal = round(coin_bal + coin_bal_lock,4)
                        continue
                    coin_total_bal = round(coin_bal + coin_bal_lock, 4)
                    pricebuff = priceupdate.PriceBuffer(market, save_log_flag=False)
                    max_num = 5
                    run_time = 0
                    priceitem = None
                    # 循环取价格，防止中间出现取价格异常
                    while (run_time <max_num and priceitem is None):
                        priceitem = pricebuff.getpriceitem(market, coin+'_btc')
                        run_time = run_time + 1

                    if priceitem is None:
                        print('coin:{0} has error to get price'.format(coin))
                        continue
                    currprice = priceitem.sell_price
                    coin_total_est_cny = round(coin_total_bal*currprice,4)
                    # 根据自己的记录得到的balance和直接查询 得到的最终lock balance可能有差异，如果lock<open order balance则是有问题的，需要查询
                    coin_open_bal = self.get_open_bal(coin).get('total_units',0)
                    # open订单的买入价格
                    coin_open_buy_amt = self.get_open_bal(coin).get('total_amount', 0)
                    # open订单的评估价格
                    coin_est_cny_open = round(self.get_open_bal(coin).get('total_units',0)*currprice,4)
                    # 检查OPEN order的UNIT和实际LOCK的UNIT是不是一致
                    if coin_bal_lock != coin_open_bal:
                        print('coin:{2},open bal:{0} is different from lock bal:{1})'.format(coin_open_bal,coin_bal_lock,coin))
                    # 实际价格评估的资产
                    coin_est_cny_all = round(coin_total_bal * currprice,4)
                    # open订单按实际买入的价格来计划金额，这个金额在每日比较会比较有用，排除价格变动造成的影响
                    coin_est_without_open = round((coin_total_bal-coin_open_bal)*currprice,4)
                    # 总的金额，正在OPEN的卖单按买入价格计算
                    coin_est_cny_ori = coin_est_without_open + coin_open_buy_amt
                    # final result
                    coin_bal_item = {'date':currdate,'coin': coin,
                                     'coin_est_cny_all': coin_est_cny_all, 'coin_est_cny_ori': coin_est_cny_ori,
                                     'coin_total_bal': coin_total_bal,'coin_open_bal': coin_open_bal, 'coin_bal_locked': coin_bal_lock,
                                     'coin_open_buy_amt':coin_open_buy_amt, 'coin_est_cny_open': coin_est_cny_open,
                                     }
                    coin_bal_item_str = json.dumps(coin_bal_item, sort_keys=True)
                    open_bal_list.append(coin_bal_item_str)
                    # ----------各个COIN总的计算金额--------------------
                    # 所有COIN的总的估算金额
                    total_est_cny = round(total_est_cny + coin_est_cny_all, 4)
                    # 所有的估算金额，OPEN订单按买入金额计算
                    total_est_cny_ori = round(total_est_cny_ori + coin_est_cny_ori, 4)
                    # open的总共买入金额
                    total_open_buy_amt = round(total_open_buy_amt + coin_open_buy_amt, 4)
                    # open的总估算金额
                    total_open_est_cny = round(total_open_est_cny + coin_est_cny_open, 4)

        # 所有COIN的结果
        total_bal = {'date': currdate, 'total_est_cny': total_est_cny, 'total_est_cny_ori': total_est_cny_ori,
                     'total_cny_bal': total_cny_bal,'total_open_buy_amt': total_open_buy_amt,
                     'total_cny_with_open': round(total_cny_bal + total_open_buy_amt,4),
                     'total_open_est_cny': total_open_est_cny}
        total_bal_str = json.dumps(total_bal, sort_keys=True)
        # 保存数据到文件
        # save summary data
        fsumary = open('daillySummary.txt','a')
        fsumary.write(total_bal_str+'\n')
        fsumary.close()
        # save detail
        fdetail = open('daillyDetail.txt','a')
        for openitem in open_bal_list:
            fdetail.write(openitem+'\n')
        fdetail.close()
        # print(total_bal)
        return total_bal
    '''得到OPEN订单的金额'''
    def get_open_bal(self, coin):
        # 总的挂单金额
        openlist = ormmysql.allopenorderlist()
        total_unit = 0
        total_amount = 0
        for openitem in openlist:
            if openitem.coin ==coin:
                total_unit = total_unit + openitem.buy_units
                total_amount = total_amount + openitem.buy_amount
        total_bal = {'total_units': round(total_unit,5), 'total_amount': round(total_amount,4)}
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
    market_list=['btc38']
    daily_summary=DailySummary(market_list)
    # daily_summary.get_open_bal('ppc')
    daily_summary.get_balance()
    # bal=daily_summary.output_summary('daily_summary.log',)
    pass