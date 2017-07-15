#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''价格获取'''
__author__='Owen_Study/owen_study@126.com'

import time
import urlaccess
import traceback
import common
import bterapi.bterclient,btc38.btc38client

'''价格管理类，根据传入的市场名称和coin获取对应的价格信息'''
class PriceManage(object):
    #传入市场名称和coin则获取对应的价格信息
    def __init__(self,market,coincode):
        self.__market=market
        self.__coincode=coincode
        self.coin_price=None
    '''返回价格明细，返回价格的对象实例'''
    def get_coin_price(self):
        # 防止调用过快，返回错误
        time.sleep(0.5)
        if self.__market=='bter':
            self.__set_bter_price()
            return self.coin_price
        elif self.__market=='btc38':
            self.__set_btc38_price()
            return self.coin_price
        else:
            raise Exception('Unknown market:%s' % self.__market)
        pass

    def __set_bter_price(self):
        bterprice=bterapi.bterclient.Client()
        pricedata_cny=bterprice.getPrice(self.__coincode + '_cny')
        try:
            if pricedata_cny.get('result')=='true':
                # cny价格的信息
                sell_cny = float(pricedata_cny.get('sell'))
                buy_cny = float(pricedata_cny.get('buy'))
                last_cny = float(pricedata_cny.get('last'))
                self.coin_price=CoinPrice(self.__coincode,buy_cny,sell_cny)
            else:
                print('获取价格错误:%s'%pricedata_cny.message)
        except Exception as e:
            exstr = traceback.format_exc()
            print(exstr)
            print(pricedata_cny)
            print(str(e))

        pass

    '''返回bter市场的价格'''
    def __set_bter_price_BAD(self):
        base_url = 'http://data.bter.com/api/1/ticker/'
        url_cny = base_url + self.__coincode + '_cny'
        url_btc = base_url + self.__coincode + '_btc'
        # 获取价格的JSONObject数据
        print('%s: is calling urlaccess.geturldata@bter'%common.CommonFunction.get_curr_time())
        pricedata_cny = urlaccess.geturldata(url_cny)
        try:
            if pricedata_cny.result=='true':
                # cny价格的信息
                sell_cny = float(pricedata_cny.sell)
                buy_cny = float(pricedata_cny.buy)
                last_cny = float(pricedata_cny.last)
                self.coin_price=CoinPrice(self.__coincode,buy_cny,sell_cny)
            else:
                print('获取价格错误:%s'%pricedata_cny.message)
        except Exception as e:
            exstr = traceback.format_exc()
            print(exstr)
            print(pricedata_cny)
            print(str(e))

    def __set_btc38_price(self):
        btc38clt=btc38.btc38client.Client()
        pricedata_cny=btc38clt.getPrice(self.__coincode + '_cny')
        # cny价格的信息
        try:
            sell_cny = pricedata_cny.ticker.get('sell')
            buy_cny = pricedata_cny.ticker.get('buy')
            last_cny = pricedata_cny.ticker.get('last')
            self.coin_price=CoinPrice(self.__coincode,buy_cny,sell_cny)
        except Exception as e:
            print(pricedata_cny)
            print(str(e))

    '''返回btc38市场的价格'''
    def __set_btc38_price_BAD(self):
        base_url = 'http://api.btc38.com/v1/ticker.php?c='
        url_cny = base_url + self.__coincode + '&mk_type=cny'
        url_btc = base_url + self.__coincode + '&mk_type=btc'
        # 获取价格的JSONObject数据
        #print('%s: is calling urlaccess.geturldata@btc38' % common.CommonFunction.get_curr_time())
        pricedata_cny = urlaccess.geturldata(url_cny)

        # cny价格的信息
        try:
            sell_cny = pricedata_cny.ticker.sell
            buy_cny = pricedata_cny.ticker.buy
            last_cny = pricedata_cny.ticker.last
            self.coin_price=CoinPrice(self.__coincode,buy_cny,sell_cny)
        except Exception as e:
            print(pricedata_cny)
            print(str(e))

'''定义价格类，多个市场之间的价格统一到同一个格式'''
class CoinPrice(object):
    '''定义初始化价格属性'''
    def __init__(self,coin_code,buy_cny,sell_cny,**kwargs):
        self.coin_code=coin_code
        self.buy_cny=buy_cny
        self.sell_cny=sell_cny
        self.last_cny=kwargs.get('last_cny',None)
        self.buy_btc=kwargs.get('buy_btc',None)
        self.sell_btc = kwargs.get('sell_btc', None)
        self.last_btc = kwargs.get('last_btc', None)
        #print('coin:%s,buy_cny:%f,sell_cny:%f' % (self.coin_code, self.buy_cny, self.sell_cny))

    def __str__(self):
        return 'coin:%s,buy_cny:%f,sell_cny:%f'%(self.coin_code,self.buy_cny,self.sell_cny)
#test
if __name__=='__main__':
    pricemanage=PriceManage('bter','doge')
    coinprice=pricemanage.get_coin_price()
    print(coinprice)
    coinprice=CoinPrice(coin_code='doge',buy_cny=222,sell_cny=3333,buy_btc=2323)
    print(coinprice)
