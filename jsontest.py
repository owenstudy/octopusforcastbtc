#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 7/25/17$ 10:59 AM$

'''注释'''

import json,cointrans


class JSONObject(object):
    def __init__(self):
        self.name = 'Ahan'
        self.email = 'www@qq.com'
        self.age = 26


if __name__ == '__main__':
    x= ['a','x','c']
    for indx,name in enumerate(x):
        print('indx:{0}, name:{1}'.format(indx,name))

    newprice = {'vash': {'price': 3, 'unit': 6}, 'xlm': {'price': 4, 'unit': 6}, 'xrp': {'price': 4, 'unit': 6}, 'emc': {'price': 2, 'unit': 6}, 'ybc': {'price': 1, 'unit': 6}, 'bts': {'price': 4, 'unit': 4}, 'wdc': {'price': 4, 'unit': 6}, 'tmc': {'price': 3, 'unit': 6}, 'xem': {'price': 4, 'unit': 6}, 'mec': {'price': 3, 'unit': 6}, 'etc': {'price': 2, 'unit': 6}, 'nxt': {'price': 3, 'unit': 6}, 'mgc': {'price': 3, 'unit': 6}, 'ncs': {'price': 4, 'unit': 6}, 'doge': {'price': 5, 'unit': 5}, 'ics': {'price': 2, 'unit': 5}, 'ltc': {'price': 2, 'unit': 6}, 'zcc': {'price': 3, 'unit': 6}, 'ardr': {'price': 4, 'unit': 6}, 'xpm': {'price': 2, 'unit': 6}, 'btc': {'price': 1, 'unit': 6}, 'eac': {'price': 5, 'unit': 4}, 'dash': {'price': 1, 'unit': 6}, 'ric': {'price': 3, 'unit': 6}, 'ppc': {'price': 2, 'unit': 6}, 'xcn': {'price': 4, 'unit': 6}, 'xzc': {'price': 2, 'unit': 6}, 'hlb': {'price': 4, 'unit': 6}, 'eth': {'price': 1, 'unit': 6}, 'blk': {'price': 3, 'unit': 6}, 'sys': {'price': 4, 'unit': 6}, 'tag': {'price': 2, 'unit': 6}, 'qrk': {'price': 4, 'unit': 6}}

    oldpricelist = {'vash': {'unit': 6, 'price': 3}, 'doge': {'unit': 5, 'price': 5}, 'dash': {'unit': 6, 'price': 1}, 'ics': {'unit': 6, 'price': 2}, 'ardr': {'unit': 6, 'price': 3}, 'sys': {'unit': 6, 'price': 4}, 'ncs': {'unit': 6, 'price': 2}, 'etc': {'unit': 5, 'price': 1}, 'nxt': {'unit': 6, 'price': 3}, 'xrp': {'unit': 6, 'price': 4}, 'bts': {'unit': 6, 'price': 4}, 'ltc': {'unit': 6, 'price': 2}, 'qrk': {'unit': 6, 'price': 3}, 'blk': {'unit': 6, 'price': 1}, 'ppc': {'unit': 6, 'price': 2}, 'tmc': {'unit': 6, 'price': 2}, 'zcc': {'unit': 6, 'price': 3}, 'btc': {'unit': 6, 'price': 1}, 'xcn': {'unit': 5, 'price': 4}, 'hlb': {'unit': 6, 'price': 4}, 'xzc': {'unit': 6, 'price': 1}, 'xem': {'unit': 6, 'price': 4}, 'mec': {'unit': 6, 'price': 3}, 'ybc': {'unit': 6, 'price': 1}, 'ric': {'unit': 6, 'price': 3}, 'eac': {'unit': 5, 'price': 5}, 'eth': {'unit': 6, 'price': 0}, 'wdc': {'unit': 6, 'price': 1}, 'xpm': {'unit': 6, 'price': 2}, 'emc': {'unit': 6, 'price': 2}, 'mgc': {'unit': 6, 'price': 2}, 'tag': {'unit': 5, 'price': 2}, 'xlm': {'unit': 6, 'price': 3}}

    for x in newprice:
        price1 = newprice.get(x).get('price')
        unit1 = newprice.get(x).get('unit')

        oldprice = oldpricelist.get(x).get('price')
        oldunit = oldpricelist.get(x).get('unit')

        if price1 != oldprice :
            print('{0}: pricenew:{1}, old_price:{2}, unitnew:{3}, unitold:{4}'.format(x, price1, oldprice, unit1, oldunit))

    priceitem = cointrans.priceitem()
    o = JSONObject()
    x = json.dumps(o, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    print(x)

