#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-8-13 上午10:13

'''注释'''

if __name__ == '__main__':
    import numpy as np
    import pandas as pd
    import pandas_datareader.data as web
    import matplotlib.pyplot as plt

    #
    # x = np.arange(0, 5, 0.1);
    # y = np.sin(x)
    # x1 = np.arange(1,4,0.5)
    # y1 = np.sin(x1)
    # plt.plot(x, y)
    # plt.plot(x1, y1)

    sp500 = web.DataReader('GS', data_source='yahoo',start='1/1/2014', end='2/16/2014')
    sp500['2d'] = np.round(pd.rolling_mean(sp500['Close'], window=2))
    sp500['10d'] = np.round(pd.rolling_mean(sp500['Close'], window=10))
    # x = sp500['Close']

    # y = pd.DatetimeIndex(x)
    # plt.plot(x,y)
    #
    print(sp500.info())
    #
    sp500[['Close','2d', '10d']].plot(grid=True, figsize=(8, 5))
    print(sp500['Close'])

    # z = pd.DataFrame()
    #
    # diff = sp500['Close'].diff()
    # diff.plot()
    plt.show()