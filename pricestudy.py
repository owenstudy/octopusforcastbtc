#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-30 下午2:30
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : pricestudy.py
# @Software: PyCharm
# ===============================================
import pandas as pd, numpy as np
import matplotlib.pyplot as plt

# 加载价格文件
aexsrcprice = pd.read_csv('btc381.txt','|')
# 给列加名字
aexsrcprice.columns=['x','pricedate','coin','buyprice','buydepth','sellprice','selldepth','mk_type','x1','x2','x3']
# 去除无用的空格
aexsrcprice['coin']=aexsrcprice['coin'].map(str.strip)
aexsrcprice['mk_type']=aexsrcprice['mk_type'].map(str.strip)
# 去除无用的列及对基础币种进行区分
aexprice = aexsrcprice[['pricedate','coin','buyprice','buydepth','sellprice','selldepth','mk_type']]
aexprice_btc = aexsrcprice[['pricedate','coin','buyprice','buydepth','sellprice','selldepth','mk_type']][aexsrcprice['mk_type']=='btc']
aexprice_cny = aexsrcprice[['pricedate','coin','buyprice','buydepth','sellprice','selldepth','mk_type']][aexsrcprice['mk_type']=='bitcny']
aexprice_usd = aexsrcprice[['pricedate','coin','buyprice','buydepth','sellprice','selldepth','mk_type']][aexsrcprice['mk_type']=='bitusd']
# 查看某个具体的coin
nxt = aexprice_cny[aexprice_cny['coin']=='nxt']




aexprice.describe()

if __name__ == '__main__':
    pass