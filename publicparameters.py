#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-19 下午9:08

import urlaccess, json,common, heapq

'''系统运行时需要用到的一些参数'''

'''取得配置文件内容,返回json字符串'''
def get_config_content():
    # 从参数表读取参数
    configf = open("config")
    configstr = ''
    for line in configf.readlines():
        configstr = configstr + line

    # 配置文件的JSON数据对象
    configjson = json.loads(configstr)

    return configjson


# 从JSON字符串中取得数据库配置信息
def get_db_string():
    # 从参数表读取参数
    # 配置文件的JSON数据对象
    configjson = get_config_content()

    databasestr = configjson.get('database')
    dbconnstr = None
    try:
        ipaddress = databasestr.get('ip')
        port =  databasestr.get('port')
        dbnamestr = databasestr.get('dbname')
        username = databasestr.get('username')
        password = databasestr.get('password')

        # 'mysql+pymysql://coin:Windows2000@192.168.1.104:3306/coins'
        dbconnstr= 'mysql+pymysql://{user}:{pwd}@{ip}:{port}/{dbname}'.format(user=username, pwd=password,\
                                                                                ip=ipaddress, port=port, dbname = dbnamestr)
        print('当前运行的DB是:{0}'.format(dbconnstr))
    except Exception as e:
        print('get db string error:'+str(e))
        dbconnstr='error'
    finally:
        return dbconnstr



# 每次交易的金额， RMB
TRANS_AMOUNT_PER_ORDER = 2
# 最大的交易池，即同时存在的最大OPEN订单数量
MAX_OPEN_ORDER_POOL = 20
# 卖出交易的止盈百分比
SELL_PROFIT_RATE = 0.012
# 价格rounding的位数,包括价格和交易单元
# ROUNDING_PRICE={'doge': {'price': 5, 'unit': 0}, 'ltc': {'price': 2, 'unit': 2}, 'btc': {'price': 1, 'unit': 5}, \
#                 'eth': {'price': 1, 'unit': 8},  'dash': {'price': 1, 'unit': 8}
#                 }

# 取消订单的时间间隔, 单位秒
CANCEL_DURATION = 1800

# each coin allow max percentage out of total open orders
COIN_MAX_RATE_IN_OPEN_ORDERS=0.35

'''从配置文件中取到一些具体的参数'''
def set_other_run_parameters():
    # 配置文件的JSON数据对象
    configjson = get_config_content()
    runconfig = configjson.get('transaction')
    global TRANS_AMOUNT_PER_ORDER
    TRANS_AMOUNT_PER_ORDER = runconfig.get('TRANS_AMOUNT_PER_ORDER', 5)
    global MAX_OPEN_ORDER_POOL
    MAX_OPEN_ORDER_POOL = runconfig.get('MAX_OPEN_ORDER_POOL', 100)
    global SELL_PROFIT_RATE
    SELL_PROFIT_RATE = runconfig.get('SELL_PROFIT_RATE', 0.012)
    global CANCEL_DURATION
    CANCEL_DURATION = runconfig.get('CANCEL_DURATION', 1800)
    global COIN_MAX_RATE_IN_OPEN_ORDERS
    COIN_MAX_RATE_IN_OPEN_ORDERS = runconfig.get('COIN_MAX_RATE_IN_OPEN_ORDERS')

# 从配置文件读取配置数据并放到全书变量中运行时需要使用
set_other_run_parameters()
# The following public parameters will not use now
# 交易的公共对象，每次交易时都调用这个对象
ORDER_LIST = []

# 文件名称
# 还没有交易完成的文件
OPEN_TRANS_FILE = 'open_trans_file'
# 已经交易完成的文件名称
CLOSED_TRANS_FILE = 'closed_trans_file'


# Get rounding setting data
def get_rounding_len(floatnum):
    # get the numbers after dot. for price
    if str(floatnum).split('.')[0] == str(floatnum):
        rounding_num = 0
    else:
        rounding_num = len('{0}'.format(floatnum).split('.')[1])
    return rounding_num


# 从网站获取所有的COIN价格信息，从价格信息中取得价格和交易单元的小数位
def get_rounding_setting(market):
    pricedata = urlaccess.get_content('http://api.btc38.com/v1/ticker.php?c=all&mk_type=cny')
    # 返回的字节转换成字符串
    price = pricedata.decode('utf8')
    pricejson= json.loads(price)
    # print(pricejson)
    coin_rounding = {}
    print('run x times')
    for coin in pricejson:
        tickers = pricejson[coin]
        if tickers is not None:
            try:
                price = tickers.get('ticker')
                if price is None or len(price) == 0:
                    continue
                else:
                    pricelow = get_rounding_len(tickers.get('ticker').get('low'))
                    pricehigh = get_rounding_len(tickers.get('ticker').get('high'))
                    pricelast = get_rounding_len(tickers.get('ticker').get('last'))
                    pricesell = get_rounding_len(tickers.get('ticker').get('sell'))
                    pricebuy = get_rounding_len(tickers.get('ticker').get('buy'))

                    pricelist = [pricelow, pricehigh, pricelast, pricesell, pricebuy]
                    # get the numbers after dot. for price
                    rounding_price_num = heapq.nlargest(1, pricelist)[0]
                    volume = tickers.get('ticker').get('vol')
                    unit_num = get_rounding_len(volume)


                coin_rounding_price = {}

                coin_rounding_price["price"] = rounding_price_num
                coin_rounding_price["unit"] = unit_num
                coin_rounding[coin]=coin_rounding_price
                # print(coin_rounding)
            except Exception as e:
                print(str(e))
                continue
    print(coin_rounding)
    return coin_rounding
# only run once and copy the string to this variable

# rounding_price = get_rounding_setting('btc38')

rounding_price_setting ={'tag': {'price': 2, 'unit': 6}, 'sys': {'price': 4, 'unit': 6}, 'ncs': {'price': 4, 'unit': 6}, 'nxt': {'price': 3, 'unit': 6}, 'mgc': {'price': 3, 'unit': 6}, 'btc': {'price': 1, 'unit': 5}, 'ltc': {'price': 2, 'unit': 6}, 'doge': {'price': 5, 'unit': 5}, 'ics': {'price': 2, 'unit': 6}, 'emc': {'price': 2, 'unit': 6}, 'blk': {'price': 3, 'unit': 6}, 'xlm': {'price': 4, 'unit': 6}, 'hlb': {'price': 4, 'unit': 6}, 'ric': {'price': 3, 'unit': 6}, 'xcn': {'price': 4, 'unit': 6}, 'etc': {'price': 2, 'unit': 6}, 'xem': {'price': 4, 'unit': 6}, 'ybc': {'price': 1, 'unit': 6}, 'eth': {'price': 1, 'unit': 6}, 'dash': {'price': 1, 'unit': 6}, 'inf': {'price': 3, 'unit': 5}, 'xzc': {'price': 2, 'unit': 6}, 'xrp': {'price': 4, 'unit': 6}, 'qrk': {'price': 4, 'unit': 6}, 'vash': {'price': 3, 'unit': 5}, 'zcc': {'price': 3, 'unit': 6}, 'xpm': {'price': 2, 'unit': 6}, 'bts': {'price': 3, 'unit': 6}, 'tmc': {'price': 3, 'unit': 5}, 'ppc': {'price': 2, 'unit': 6}, 'wdc': {'price': 4, 'unit': 6}, 'mec': {'price': 3, 'unit': 6}, 'eac': {'price': 5, 'unit': 5}, 'ardr': {'price': 4, 'unit': 5}}



# 价格rounding规则
def rounding_price(coin):
    rounding_data = rounding_price_setting.get(coin)
    if rounding_data == None:
        return 2
    else:
        return rounding_data.get('price', 2)
# UNIT的ROUNDING规则
def rounding_unit(coin):
    rounding_data = rounding_price_setting.get(coin)
    if rounding_data == None:
        return 2
    else:
        return rounding_data.get('unit', 2)

if __name__ == '__main__':
    # get_db_string()
    get_rounding_setting('btc38')
    x = rounding_price('wdc')
    y = rounding_unit('ltc')
    print('{0}:{1}'.format(x,y))
    pass