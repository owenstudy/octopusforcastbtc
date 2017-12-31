#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-30 下午2:30
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : pricestudy.py
# @Software: PyCharm
# ===============================================
import pandas as pd, numpy as np

# 加载价格文件
aexsrcprice = pd.read_csv('btc38.txt','|')
# 给列加名字
aexsrcprice.columns=['X','pricedate','coin','buyprice','buydepth','sellprice','selldepth','x1','x2','x3']
# 去除无用的列
aexprice = aexsrcprice[['pricedate','coin','buyprice','buydepth','sellprice','selldepth']]
# 去除无用的空格
aexsrcprice['coin']=aexsrcprice['coin'].map(str.strip)


aexprice.describe()

if __name__ == '__main__':
    pass