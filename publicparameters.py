#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-19 下午9:08

import urlaccess, json,common

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
                    price = tickers.get('ticker').get('low')
                    volume = tickers.get('ticker').get('vol')
                # get the numbers after dot. for price
                if str(price).split('.')[0] == str(price):
                    rounding_num = 0
                else:
                    rounding_num = len('{0}'.format(price).split('.')[1])
                # for unit rounding
                if str(volume).split('.')[0] == str(volume):
                    unit_num = 0
                else:
                    unit_num = len('{0}'.format(volume).split('.')[1])

                coin_rounding_price = {}

                coin_rounding_price["price"] = rounding_num
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

rounding_price_setting={'vash': {'unit': 6, 'price': 3}, 'doge': {'unit': 5, 'price': 5}, 'dash': {'unit': 6, 'price': 1}, 'ics': {'unit': 6, 'price': 2}, 'ardr': {'unit': 6, 'price': 3}, 'sys': {'unit': 6, 'price': 4}, 'ncs': {'unit': 6, 'price': 2}, 'etc': {'unit': 5, 'price': 1}, 'nxt': {'unit': 6, 'price': 3}, 'xrp': {'unit': 6, 'price': 4}, 'bts': {'unit': 6, 'price': 4}, 'ltc': {'unit': 6, 'price': 2}, 'qrk': {'unit': 6, 'price': 3}, 'blk': {'unit': 6, 'price': 1}, 'ppc': {'unit': 6, 'price': 2}, 'tmc': {'unit': 6, 'price': 2}, 'zcc': {'unit': 6, 'price': 3}, 'btc': {'unit': 6, 'price': 1}, 'xcn': {'unit': 5, 'price': 4}, 'hlb': {'unit': 6, 'price': 4}, 'xzc': {'unit': 6, 'price': 1}, 'xem': {'unit': 6, 'price': 4}, 'mec': {'unit': 6, 'price': 3}, 'ybc': {'unit': 6, 'price': 1}, 'ric': {'unit': 6, 'price': 3}, 'eac': {'unit': 5, 'price': 5}, 'eth': {'unit': 6, 'price': 0}, 'wdc': {'unit': 6, 'price': 1}, 'xpm': {'unit': 6, 'price': 2}, 'emc': {'unit': 6, 'price': 2}, 'mgc': {'unit': 6, 'price': 2}, 'tag': {'unit': 5, 'price': 2}, 'xlm': {'unit': 6, 'price': 3}}
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
    get_db_string()
    # get_rounding_setting('doge')
    x = rounding_price('btc')
    y = rounding_unit('btc')
    print('{0}:{1}'.format(x,y))
    pass