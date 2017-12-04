#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-3 下午10:15
# @Author  : Owen_study
# @Email   : owen_study@163.com
# @File    : btcwexclient.py
# @Software: PyCharm
# ===============================================

from config import wex_apiconfig
from config import base_currency
import wex.client,common

'''统一接口'''
#test api transaction
key=wex_apiconfig.get("key")
secret=wex_apiconfig.get("secret")
accountid=wex_apiconfig.get("accountid")


class Client():
    def __init__(self):
        #获取API信息
        self.btcwexclt = wex.client.Client(key, secret, accountid)
        # 基础的交易货币
        self.basecurrcode = base_currency.get('basecurrcode','btc')

        pass

    '''得到市场的深度'''
    def getMarketDepth(self,coin_code,mk_type='btc'):
        try:
            data = self.btcwexclt.getDepth(mk_type,coin_code)
            # 买单列表
            buylist=list(data.get(coin_code+'_'+mk_type).get('bids'))
            # 卖单列表
            selllist=list(data.get(coin_code+'_'+mk_type).get('asks'))

            depthlist=common.JSONObject({'date':common.get_curr_time_str(),'sell':selllist,'buy':buylist})
        except Exception as e:
            # print(str(e))
            depthlist= None
        return depthlist


if __name__ == '__main__':
    clt = Client()
    depth = clt.getMarketDepth('ltc','btc')
    print(depth)
    pass