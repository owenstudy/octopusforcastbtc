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
    priceitem = cointrans.priceitem()
    o = JSONObject()
    x = json.dumps(o, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    print(x)
