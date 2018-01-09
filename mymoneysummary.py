#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 18-1-6 上午8:38
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : mymoneysummary.py
# @Software: PyCharm
# ===============================================
# 计算帐户中的余额,以不同的单位进行评估,btc, cny, usd
import ordermanage,common

summary_file = 'my_money_summary.txt'

def gen_money_summary():
    # 市场的交易处理器
    order_market = ordermanage.OrderManage('btc38')
    # 所有的余额
    mybal = order_market.getMyBalance()
    mybaldate = common.get_curr_time_str()
    # 计算当前时间的评估价格
    currallprice_btc = order_market.getMarketPrice('all_btc')
    currallprice_cny = order_market.getMarketPrice('all_bitcny')
    currallprice_usd = order_market.getMarketPrice('all_bitusd')

    total_bal_cny = 0
    # RMB价格
    btcprice_cny = currallprice_cny.get('btc').get('ticker').get('buy')
    # USD价格
    btcprice_usd = currallprice_usd.get('btc').get('ticker').get('buy')
    for coin in mybal:
        coinbal = mybal.get(coin).get('available')+ mybal.get(coin).get('locked')
        if coinbal == 0:
            continue
        if coin == 'bitcny':
            total_bal_cny = total_bal_cny + coinbal
            pass
        elif coin == 'bitusd':
            # 把USD转换成btc后再转换成cny来计算
            total_bal_cny = total_bal_cny + coinbal/btcprice_usd*btcprice_cny
            pass
        elif coin == 'btc':
            total_bal_cny = total_bal_cny + coinbal*btcprice_cny
        else:
            # btc定价的价格
            try:
                coinprice_btc = currallprice_btc.get(coin).get('ticker').get('buy')
                if coinprice_btc is not None:
                    # 转换成btc的数量
                    coinbal_btc = coinbal * coinprice_btc
                    # 转换成RMB的价格
                    total_bal_cny = total_bal_cny + coinbal_btc * btcprice_cny
            except Exception as e:
                # 不再支持交易的coin
                if coin == 'ybc' or coin == 'nss':
                    pass
                else:
                    print('{0} price error:{1}'.format(coin,str(e)))
    total_bal_cny = round(total_bal_cny,2)
    print('{0}: balance_cny: {1}'.format(mybaldate,total_bal_cny))
    # 保存结果到文件
    balfile = open(summary_file,'a')
    mybalancesummary = '{0}:{1}\n'.format(mybaldate,total_bal_cny)
    balfile.write(mybalancesummary)
    balfile.close()
    return total_bal_cny
    pass



if __name__ == '__main__':
    gen_money_summary()
    pass