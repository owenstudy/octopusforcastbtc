#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 8/1/17$ 1:19

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import common

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
forecast_verify_list ={}
for indx, line in enumerate(open('ForecaseData.txt','r').readlines()):
    forecast_time = line.split(': ')[0]
    forecast_items = line.split(': ')[1].split(',')
    coin = forecast_items[0].split(':')[1]
    verify_cnt = forecast_items[1].split(':')[1]
    verify_cnt = int(verify_cnt)
    rate = forecast_items[3].split(':')[1]
    rate = float(rate.split('\n')[0])
    if indx ==0:
        start_time = forecast_time
    else:
        end_time = forecast_time
    if forecast_rate_list.get(coin) is None:
        ratelist = []
        ratelist.append(rate)
        verify_list =[]
        verify_list.append(verify_cnt)
        forecast_rate_list[coin] = ratelist
        forecast_verify_list[coin] = verify_list
    else:

        forecast_rate_list.get(coin).append(rate)
        forecast_verify_list.get(coin).append(verify_cnt)
coinratelist = forecast_rate_list.get('nxt_cny')
coinverifycntlist=forecast_verify_list.get('nxt_cny')
# ts = pd.Series(doge, index=pd.date_range(start=common.CommonFunction.strtotime(start_time),end=common.CommonFunction.strtotime(end_time)))
# ts = ts.std()
# print(ts)

# rate list
dtrange = pd.date_range(start=start_time,periods=len(coinratelist), freq='0.1H')
print(dtrange)
ts = pd.Series(coinratelist,index=dtrange)

ts=ts.diff()
ts.plot()
plt.show()

# verify cnt list
dtrange = pd.date_range(start=start_time,periods=len(coinverifycntlist), freq='0.1H')
print(coinverifycntlist)
ts = pd.Series(coinverifycntlist,index=dtrange)

ts=ts.diff()
ts.plot()
plt.show()


# 正态分布
mu = 0
sigma = 1 # standard deviation
x = np.arange(-5,5,0.1)

# y = stats.norm.pdf(x, 0, 1)

# plt.plot(x, y )
# plt.show()