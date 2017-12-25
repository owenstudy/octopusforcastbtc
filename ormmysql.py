#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 7/24/17 1:14 PM

from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.sql.expression import Cast
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import or_, func
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR
import cointrans, json, btc38.btc38client
import common, priceupdate
import publicparameters

# 表的属性描述对象
metadata = MetaData()

# 从类OrderItem中自动来生成
# 调用方法
#       orderitem = OrderItem('btc38', 'doge')
#       orderitem.gen_table_class()
# 生成后调整类型, priceitem(1000)
# table class
OrderItemTable = Table(
    "t_coin_trans", metadata,
    Column('trans_id', INTEGER, primary_key=True),
    Column('market', VARCHAR(100)),
    Column('coin', VARCHAR(100)),
    Column('buy_order_id', INTEGER),
    Column('buy_status', VARCHAR(100)),
    Column('buy_date', VARCHAR(100)),
    Column('buy_price', FLOAT),
    Column('buy_units', FLOAT),
    Column('buy_amount', FLOAT),
    Column('sell_order_id', INTEGER),
    Column('sell_status', VARCHAR(100)),
    Column('sell_date', VARCHAR(100)),
    Column('sell_price', FLOAT),
    Column('sell_units', FLOAT),
    Column('sell_amount', FLOAT),
    Column('priceitem', VARCHAR(1000))
)
OrderItemTableLog = Table(
    "t_coin_trans_log", metadata,
    Column('trans_id', INTEGER, primary_key=True),
    Column('market', VARCHAR(100)),
    Column('coin', VARCHAR(100)),
    Column('buy_order_id', INTEGER),
    Column('buy_status', VARCHAR(100)),
    Column('buy_date', VARCHAR(100)),
    Column('buy_price', FLOAT),
    Column('buy_units', FLOAT),
    Column('buy_amount', FLOAT),
    Column('sell_order_id', INTEGER),
    Column('sell_status', VARCHAR(100)),
    Column('sell_date', VARCHAR(100)),
    Column('sell_price', FLOAT),
    Column('sell_units', FLOAT),
    Column('sell_amount', FLOAT),
    Column('priceitem', VARCHAR(1000))
)

# 视图,所有DB的open order
OpenOrderView = Table(
    "v_coin_trans_all", metadata,
    Column('trans_id', INTEGER, primary_key=True),
    Column('market', VARCHAR(100)),
    Column('coin', VARCHAR(100)),
    Column('buy_order_id', INTEGER),
    Column('buy_status', VARCHAR(100)),
    Column('buy_date', VARCHAR(100)),
    Column('buy_price', FLOAT),
    Column('buy_units', FLOAT),
    Column('buy_amount', FLOAT),
    Column('sell_order_id', INTEGER),
    Column('sell_status', VARCHAR(100)),
    Column('sell_date', VARCHAR(100)),
    Column('sell_price', FLOAT),
    Column('sell_units', FLOAT),
    Column('sell_amount', FLOAT),
    Column('priceitem', VARCHAR(1000))
)
# 网站交易的历史记录
OrderTransList = Table(
    "t_aex_trans", metadata,
    Column('trans_id', INTEGER, primary_key=True),
    Column('id', INTEGER),
    Column('coin', VARCHAR(100)),
    Column('price', FLOAT),
    Column('volume', FLOAT),
    Column('btcvolume', FLOAT),
    Column('buyer_id', VARCHAR(100)),
    Column('seller_id', VARCHAR(100)),
    Column('trans_time', VARCHAR(100),)
)

# 定投相关的表,总表
RegularInvestSummary = Table(
    "t_regular_invest_summary", metadata,
    Column('account_id', INTEGER, primary_key=True),
    Column('coin_pair', VARCHAR(100)),
    Column('unit_balance', FLOAT),
    Column('unit_amount', FLOAT),
    Column('esti_unit_amount', FLOAT),
    Column('esti_profit_rate', FLOAT),
    Column('total_units', FLOAT),
    Column('total_amount', FLOAT),
    Column('total_profit', FLOAT)
)
# 定投相关的表,明细
RegularInvestDetail = Table(
    "t_regular_invest_dtl", metadata,
    Column('trans_id', INTEGER, primary_key=True),
    Column('account_id', INTEGER),
    Column('trans_order_id', INTEGER),
    Column('trans_type', VARCHAR(4)),
    Column('coin_pair', VARCHAR(100)),
    Column('trans_price', FLOAT),
    Column('trans_units', FLOAT),
    Column('trans_amount', FLOAT),
    Column('trans_date', VARCHAR(100))
)# 定投相关的表,明细日志
RegularInvestDetailLog = Table(
    "t_regular_invest_dtl_log", metadata,
    Column('trans_id', INTEGER, primary_key=True),
    Column('account_id', INTEGER),
    Column('trans_order_id', INTEGER),
    Column('trans_type', VARCHAR(4)),
    Column('coin_pair', VARCHAR(100)),
    Column('trans_price', FLOAT),
    Column('trans_units', FLOAT),
    Column('trans_amount', FLOAT),
    Column('trans_date', VARCHAR(100))
)

    # 创建数据库连接,MySQLdb连接方式
# My laptop PC DB
# mysql_db = create_engine('mysql+pymysql://coin:Windows2000@127.0.0.1:3306/coins', echo = False)
# My home PC db
# mysql_db = create_engine('mysql+pymysql://coin:Windows2000@192.168.1.104:3306/coins')
connstr = publicparameters.get_db_string()
mysql_db = create_engine(connstr)
# 创建数据库连接，使用 mysql-connector-python连接方式
# 生成表
metadata.create_all(mysql_db)

# 创建一个映射类,one table one class
class MapperOrder(object):
    pass
# 创建一个映射类,one table one class
class MapperOrderLog(object):
    pass
# 所有DB中的open order列表
class MapperAllOpenView(object):
    pass

# 所有aex网站中的交易历史
class MapperOrderTransList(object):
    pass

# 定投的总表
class MapperRegularInvestSummary(object):
    pass
# 定投的明细
class MapperRegularInvestDetail(object):
    pass
# 定投的明细log
class MapperRegularInvestDetailLog(object):
    pass



# 把表映射到类
mapper(MapperOrder, OrderItemTable)
# 映射到LOG表
mapper(MapperOrderLog, OrderItemTableLog)
# 所有DB中的open order列表
mapper(MapperAllOpenView, OpenOrderView)
# 所有aex网站中的交易历史
mapper(MapperOrderTransList, OrderTransList)
# 定投的总表
mapper(MapperRegularInvestSummary, RegularInvestSummary)
# 定投的明细
mapper(MapperRegularInvestDetail, RegularInvestDetail)
# 定投的明细log
mapper(MapperRegularInvestDetailLog, RegularInvestDetailLog)


# 创建了一个自定义了的 Session类
Session = sessionmaker()
# 将创建的数据库连接关联到这个session
Session.configure(bind=mysql_db)
session = Session()
# class object to dict
def convert_to_builtin_type(obj):
    d = {}
    d.update(obj.__dict__)
    return d
# order to table record
def ordertorecord(orderitem, orderrecord):
    # save all the properties to table columns
    # trans_id 直接从业务交易表中取得，放到LOG表中
    # orderrecord.trans_id = orderitem.trans_id
    # Class property is same as table column name
    orderrecord.market = orderitem.market
    orderrecord.buy_order_id = orderitem.buy_order_id
    orderrecord.buy_date = orderitem.buy_date
    orderrecord.coin = orderitem.coin
    orderrecord.buy_price = orderitem.buy_price
    orderrecord.buy_units = orderitem.buy_units
    orderrecord.buy_amount = orderitem.buy_amount
    orderrecord.buy_status = orderitem.buy_status
    orderrecord.sell_order_id = orderitem.sell_order_id
    orderrecord.sell_date = orderitem.sell_date
    orderrecord.sell_price = orderitem.sell_price
    orderrecord.sell_units = orderitem.sell_units
    orderrecord.sell_amount = orderitem.sell_amount
    orderrecord.sell_status = orderitem.sell_status
    # covert the priceitem object to json string
    # pricedatestr = common.CommonFunction.datetimetostr(orderitem.priceitem.pricedate)

    o=convert_to_builtin_type(orderitem.priceitem)
    priceitemstr= json.dumps(o, default=convert_to_builtin_type, sort_keys=True, indent=4)
    orderrecord.priceitem = priceitemstr

    return orderrecord
def recordtoorder(orderrecord,orderitem):
    # save all the properties to table columns
    # trans_id 直接从业务交易表中取得，放到LOG表中
    # orderrecord.trans_id = orderitem.trans_id
    # Class property is same as table column name
    orderitem.market = orderrecord.market
    orderitem.buy_order_id = orderrecord.buy_order_id
    orderitem.buy_date = orderrecord.buy_date
    orderitem.coin = orderrecord.coin
    orderitem.buy_price = orderrecord.buy_price
    orderitem.buy_units = orderrecord.buy_units
    orderitem.buy_amount = orderrecord.buy_amount
    orderitem.buy_status = orderrecord.buy_status
    orderitem.sell_order_id = orderrecord.sell_order_id
    orderitem.sell_date = orderrecord.sell_date
    orderitem.sell_price = orderrecord.sell_price
    orderitem.sell_units = orderrecord.sell_units
    orderitem.sell_amount = orderrecord.sell_amount
    orderitem.sell_status = orderrecord.sell_status
    # covert  json string to priceitem object
    priceitemstr = orderrecord.priceitem
    if priceitemstr is not None:
        # pricedate, coin,buy_price, buy_depth, sell_price, sell_depth)
        priceitemdict = json.loads(priceitemstr)
        priceitemobj = common.JSONObject(priceitemdict)
        priceitem = priceupdate.PriceItem(priceitemobj.pricedate, priceitemobj.coin, priceitemobj.buy_price, priceitemobj.buy_depth, \
                priceitemobj.sell_price, priceitemobj.sell_depth)
        orderitem.priceitem = priceitem

    return orderitem

# 保存一个新的order
def saveorder(orderitem =None):
    try:
        neworderrecord = MapperOrder()
        # save to record to database
        ordertorecord(orderitem, neworderrecord)
        # submit order to db
        session.add(neworderrecord)
        session.flush()
        session.commit()

        return True
        pass
    except Exception as e:
        print('Save to DB error:{0}'.format(str(e)))
        return False

# 保存一个新的order
def saveorderlog(orderitem=None):
    try:
        neworderrecordlog = MapperOrderLog()
        query = session.query(MapperOrder)
        # save to record to database
        ordertorecord(orderitem, neworderrecordlog)
        # Find the trans_id
        x=query.filter_by(coin=orderitem.coin, buy_date =orderitem.buy_date).first()
        trans_id = x.trans_id

        # Get the trans_id from trans table
        neworderrecordlog.trans_id = trans_id

        # submit order to db
        session.add(neworderrecordlog)
        session.flush()
        session.commit()

        return True
        pass
    except Exception as e:
        print('Save to DB log error:{0}'.format(str(e)))
        return False


# 更新一个order
def updateorder(orderitem):
    try:
        # Find the record in DB
        query = session.query(MapperOrder)
        # coin and buy_date is unique
        orderrecord=query.filter_by(coin=orderitem.coin, buy_date=orderitem.buy_date).first()

        ordertorecord(orderitem, orderrecord)
        # orderrecord.buy_status='closed'
        session.commit()
        return True
    except Exception as e:
        print('Update order error:{0}'.format(str(e)))
        return False
# delete order from DB
def delorder(orderitem):
    try:
        # Find the record in DB
        query = session.query(MapperOrder)
        # coin and buy_date is unique
        orderrecord=query.filter_by(coin=orderitem.coin, buy_date=orderitem.buy_date)
        # 删除之前备份到LOG表
        saveorderlog(orderitem)
        # remove
        orderrecord.delete()
        # commit to db
        session.commit()
        return True
    except Exception as e:
        print('Del order error:{0}'.format(str(e)))
        return False
# 得到OPEN 记录的数量
def openordercount():
    # Find the record in DB
    query = session.query(MapperOrder)
    # coin and buy_date is unique
    opencount=query.filter(or_(MapperOrder.sell_status=='open', MapperOrder.sell_status ==None)).count()
    # print(opencount)
    return opencount
    pass

# 获取open order list，把记录转换成列表以便在程序中进行处理
def openorderlist():
    # Find the record in DB
    query = session.query(MapperOrder)
    orderlist = []

    # coin and buy_date is unique
    for orderrecord in query.filter(or_(MapperOrder.sell_status=='open', MapperOrder.sell_status == None)):
        orderitem = cointrans.OrderItem('x', 'y')
        recordtoorder(orderrecord, orderitem)
        orderlist.append(orderitem)
    return orderlist
# 从视图中获取所有DB的OPEN ORDER列表
def allopenorderlist():
    # Find the record in DB
    query = session.query(MapperAllOpenView)
    orderlist = []

    # coin and buy_date is unique
    for orderrecord in query.filter(or_(MapperAllOpenView.sell_status=='open', MapperAllOpenView.sell_status == None)):
        orderitem = cointrans.OrderItem('x', 'y')
        recordtoorder(orderrecord, orderitem)
        orderlist.append(orderitem)
    return orderlist
# 保存从aex网站获取的交易数据
def saveaextrans(transitem):
    query = session.query(MapperOrderTransList)
    # 检查记录是不是存在，如果不存在则保存
    existing_trans = query.filter_by(id=transitem.id).first()
    if existing_trans is None:
        newtransitem = MapperOrderTransList()
        newtransitem.id=transitem.id
        newtransitem.coin=transitem.coin
        newtransitem.price=transitem.price
        newtransitem.volume=transitem.volume
        newtransitem.btcvolume=transitem.btcvolume
        newtransitem.buyer_id=transitem.buyer_id
        newtransitem.seller_id=transitem.seller_id
        newtransitem.trans_time=transitem.trans_time
        # submit order to db
        session.add(newtransitem)
        session.flush()
        session.commit()
    pass
# 生成定投的交易帐户
def save_regular_account(coin_pair):
    # TODO
    # 判断是不是存在帐户,如果不存在则新增加,否则就不创建
    exist_account = get_regular_invest_summary(coin_pair)
    if exist_account is None:
        newaccount = MapperRegularInvestSummary()
        newaccount.coin_pair = coin_pair
        # 默认的帐户余额为0
        newaccount.unit_balance = 0
        newaccount.unit_amount = 0
        newaccount.total_units = 0
        newaccount.total_amount = 0
        newaccount.total_profit = 0

        session.add(newaccount)
        session.flush()
        session.commit()
        # 保存成功后再查询返回
        exist_account = get_regular_invest_summary(coin_pair)
    return exist_account
    pass

# 保存定期投资的交易记录
def save_regular_invest(orderitem=None):
    # TODO
    # 先默认为btc帐户,以后再扩展支持到cny, usd等
    coin_pair = orderitem.coin_pair
    regular_account = save_regular_account(coin_pair)
    # 帐户存在或者创建成功后才执行后续的交易保存操作
    if regular_account is not None:
        newtrans = MapperRegularInvestDetail()
        newtrans.account_id = regular_account.get('account_id')
        newtrans.coin_pair = coin_pair
        # 根据交易的字段判断是买入或者是卖出
        if orderitem.sell_price is not None:
            newtrans.trans_type = 'sell'
            # 卖出交易的明细信息
            newtrans.trans_order_id = orderitem.sell_order_id
            newtrans.trans_price = orderitem.sell_price
            newtrans.trans_units = orderitem.sell_units*-1
            newtrans.trans_amount = orderitem.sell_amount*-1
            newtrans.trans_date = orderitem.sell_date
            trans_units = orderitem.sell_units*-1
            # 卖出保存为负数
            trans_amount = orderitem.sell_amount*-1
        else:
            newtrans.trans_type = 'buy'
            # 卖出交易的明细信息
            newtrans.trans_order_id = orderitem.buy_order_id
            newtrans.trans_price = orderitem.buy_price
            newtrans.trans_units = orderitem.buy_units
            newtrans.trans_amount = orderitem.buy_amount
            newtrans.trans_date = orderitem.buy_date
            trans_units = orderitem.buy_units
            # 卖出保存为负数
            trans_amount = orderitem.buy_amount
            pass
        session.add(newtrans)
        # 把本次交易的金额汇总到总表中
        query = session.query(MapperRegularInvestSummary)
        accountinfo = query.filter_by(coin_pair=coin_pair).first()
        accountinfo.unit_balance = accountinfo.unit_balance+trans_units
        accountinfo.unit_amount = accountinfo.unit_amount+trans_amount
        # 累积的金额更新
        if newtrans.trans_type == 'buy':
            accountinfo.total_units = accountinfo.total_units + trans_units
            accountinfo.total_amount = accountinfo.total_amount + trans_amount
        else:
            # 卖出后对当前的金额进行清空操作,都设置为0,重新开始新一轮的定投
            accountinfo.unit_balance = 0
            accountinfo.unit_amount = 0
            # 盈利的金额为正,亏损的为负,只有卖出时才把盈利的金额更新上去
            accountinfo.total_profit = -1*(accountinfo.total_profit + accountinfo.unit_amount + trans_amount)

        # 评估金额更新
        accountinfo.esti_unit_amount = accountinfo.unit_balance*newtrans.trans_price
        accountinfo.esti_profit_rate = round(accountinfo.esti_unit_amount/accountinfo.unit_amount - 1,3)
        session.commit()
        # 把所有的买入记录清空,保存到log表中
        # TODO
# 更新当前已购买的估值
def update_invest_estivalue(coin_pair, priceitem):
    query = session.query(MapperRegularInvestSummary)
    accountinfo = query.filter_by(coin_pair=coin_pair).first()
    # 评估金额更新
    accountinfo.esti_unit_amount = accountinfo.unit_balance * priceitem.sell_price
    if accountinfo.unit_amount == 0:
        accountinfo.esti_profit_rate = 0
    else:
        accountinfo.esti_profit_rate = round(accountinfo.esti_unit_amount / accountinfo.unit_amount - 1, 3)
    session.commit()

    pass
# 把现表的数据保存到LOG表中
def save_invest_log(coin_pair):
    accountinfo = get_regular_invest_summary(coin_pair)
    pass
# 获取最近的交易日期
def get_last_invest_date(coin_pair):
    accountinfo = get_regular_invest_summary(coin_pair)
    # 帐户不存在,则返回值为空
    if accountinfo is None:
        result = {'last_trans_date': None}
        return result

    query = session.query(func.max(MapperRegularInvestDetail.trans_date))
    result = None
    # 查询所有的买入记录,找到最近一次交易的记录
    last_trans = query.filter(MapperRegularInvestDetail.account_id==accountinfo.get('account_id')).all()
    for trans in last_trans:
        result = {'last_trans_date': trans[0]}
    return result
    pass
# 获取定期投资的相关信息,传入指定的COIN对
def get_regular_invest_summary(coin_pair):
    # TODO
    query = session.query(MapperRegularInvestSummary)
    # coin_pair一个COIN只有 一个帐户
    accountinfo = query.filter_by(coin_pair=coin_pair)
    result = None
    for account in accountinfo:
        result = {'account_id':account.account_id, 'unit_balance':account.unit_balance, 'unit_amount':account.unit_amount}
    # print(result)
    return result
    pass

def ormtest():

    # save_regular_account('ltc_btc')
    # get_last_invest_record('ltc_btc')
    # account = get_regular_invest_summary('ltc_btc')
    # orderitem = cointrans.OrderItem('btc38','ltc')
    # orderitem.buy_price=0.01111
    # orderitem.buy_amount=0.001
    # orderitem.buy_units = 1
    # orderitem.buy_date = common.get_curr_time_str()
    # orderitem.buy_order_id=1001
    # save_regular_invest(orderitem)
    # orderitem_sell = cointrans.OrderItem('btc38','ltc')
    # orderitem_sell.sell_price=0.015
    # orderitem_sell.sell_amount=0.001
    # orderitem_sell.sell_units = 2
    # orderitem_sell.sell_date = common.get_curr_time_str()
    # orderitem_sell.sell_order_id=1002
    # save_regular_invest(orderitem_sell)

    # test save aex trans list
    # client = btc38.btc38client.Client()
    # trade_list = client.getMyTradeList('bcc_btc')
    # for transitem  in trade_list:
    #     aextransitem = cointrans.AEXTransItem(transitem)
    #     saveaextrans(aextransitem)

    # test save order
    # orderitem = cointrans.OrderItem('btc38','ltc')
    #
    # orderitem.buy_order_id = 1234
    # orderitem.buy_status = 'open'
    # orderitem.buy_price = 1.1222
    # orderitem.buy_amount = 20
    # orderitem.buy_units = 18
    # orderitem.buy_date = common.get_curr_time_str()
    #
    pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
    priceitem = pricebuffer.getpriceitem('btc38', 'ltc_btc')
    update_invest_estivalue('ltc_btc',priceitem)
    # #
    # orderitem.priceitem = priceitem
    #
    # saveorder(orderitem)
    # saveorderlog(orderitem)
    # updateorder(orderitem)
    # delorder(orderitem)
    # openordercount()
    openorderlist()



if __name__ == '__main__':
    pass
    ormtest()
