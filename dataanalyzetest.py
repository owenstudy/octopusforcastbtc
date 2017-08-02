#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 8/1/17$ 1:19

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

s = pd.Series([1,3,5,np.nan, 6, 8])
print(s)

dates = pd.date_range('20130101', periods=6)
print(dates)

df = pd.DataFrame(np.random.randn(6,4), index=dates, columns=list('ABCD'))

print(df)

ts = pd.Series([1,3,4,5,8,10,2,3], index=pd.date_range('1/1/2000', periods=8))
ts = ts.diff()
# ts.plot()
# plt.show()

forecast_rate_list={}
for line in open('ForecaseData.txt','r').readlines():
    forecast_time = line.split(': ')[0]
    forecast_items = line.split(': ')[1].split(',')
    coin = forecast_items[0].split(':')[1]
    rate = forecast_items[3].split(':')[1]
    rate = float(rate.split('\n')[0])
    if forecast_rate_list.get(coin) is None:
        ratelist = []
        ratelist.append(rate)
        forecast_rate_list[coin] = ratelist
    else:

        forecast_rate_list.get(coin).append(rate)
doge = forecast_rate_list.get('ardr_cny')
print(doge)
ts = pd.Series(doge, index=pd.date_range('1/8/2017', periods=len(doge)))
# ts = ts.std()
print(ts)
ts = pd.Series(doge, index=pd.date_range('8/1/2017', periods=len(doge),freq='0.5H' ))

ts=ts.describe()
ts.plot()
plt.show()


# 正态分布
mu = 0
sigma = 1 # standard deviation
x = np.arange(-5,5,0.1)

y = stats.norm.pdf(x, 0, 1)

plt.plot(x, y )
plt.show()