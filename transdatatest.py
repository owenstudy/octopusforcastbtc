#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-8-5 上午11:50

import ordermanage, ormmysql
'''注释'''



if __name__ == '__main__':
    order_market = ordermanage.OrderManage('btc38')

    open_order_list_web = order_market.getOpenOrderList('zcc')
    open_order_list_db = ormmysql.allopenorderlist()
    for openorder in open_order_list_web:
        coin = openorder.coin_code_pair
        order_id_web = int(openorder.order_id)
        order_units_web = float(openorder.trans_unit)
        for dbopenorder in open_order_list_db:
            order_id_db = dbopenorder.sell_order_id
            order_units_db = dbopenorder.sell_units
            if order_id_web == order_id_db:
                if order_units_web == order_units_db:
                    break
                else:
                    print('{0}, order_id:{1}, order_unts_web:{2}, order_units_db{3}'.format(coin,
                                                                                                                order_id_db,
                                                                                                                order_units_web,
                                                                                                                order_units_db))
                    break
        else:
            print('{0} did not find in db, order_id:{1}'.format(coin,order_id_db))

    for dbopenorder in open_order_list_db:
        coin = dbopenorder.coin
        order_id_db = dbopenorder.sell_order_id
        order_units_db = dbopenorder.sell_units
        for webopenorder in open_order_list_web:
            order_id_web = int(webopenorder.order_id)
            order_units_web = float(webopenorder.trans_unit)
            if order_id_web == order_id_db:
                if order_units_web == order_units_db:
                    break
                else:
                    print('{0}, order_id:{1}, order_unts_web:{2}, order_units_db{3}'.format(coin,
                                                                                                                 order_id_web,
                                                                                                                 order_units_web,
                                                                                                                 order_units_db))
                    break
        else:
            print('{0} did not find in web, order_id:{1}'.format(coin,order_id_web))
    status = order_market.getOrderStatus('368163721','sys')

    print(status)
    pass