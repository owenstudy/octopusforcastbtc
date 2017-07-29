#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-28 下午11:21

from  priceupdate import MonitorPrice

'''运行'''

def run():
    # 开始调用实例去开始运行
    monitor_coin = MonitorPrice()
    monitor_coin.check_best_coin()


if __name__ == '__main__':
    run()

    pass