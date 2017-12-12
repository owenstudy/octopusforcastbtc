#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Time    : 17-12-8 下午9:38
# @Author  : Owen_study
# @Email   : owen_study@126.com
# @File    : sms.py
# @Software: PyCharm
# ===============================================

import requests, json
import config

'''发送SMS信息'''
def sms_send(mobile, message):
    apikey = config.sms_auth.get("apikey")
    resp = requests.post("http://sms-api.luosimao.com/v1/send.json", \
                         auth=("api",apikey),\
                         data={"mobile":mobile, "message":message+"【水果尝尝鲜】"}, timeout=3)
    result = resp.content
    print(result)

if __name__ == '__main__':
    sms_send(13166366407, "coin up great, 15%")
    pass