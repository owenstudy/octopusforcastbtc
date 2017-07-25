#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 7/24/17 1:14 PM

from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.sql.expression import Cast
from sqlalchemy.ext.compiler import compiles
from sqlalchemy import or_
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR
import cointrans, json
import common, priceupdate

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

# 创建数据库连接,MySQLdb连接方式
mysql_db = create_engine('mysql+pymysql://coin:Windows2000@127.0.0.1:3306/coins')
# 创建数据库连接，使用 mysql-connector-python连接方式
# 生成表
metadata.create_all(mysql_db)

# 创建一个映射类,one table one class
class MapperOrder(object):
    pass

# 把表映射到类
mapper(MapperOrder, OrderItemTable)
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
    # trans_id to generate automatically
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
    o=convert_to_builtin_type(orderitem.priceitem)
    priceitemstr= json.dumps(o, default=convert_to_builtin_type, sort_keys=True, indent=4)
    orderrecord.priceitem = priceitemstr

    return orderrecord

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
    print(opencount)
    return opencount
    pass

def test():
    # test save order
    orderitem = cointrans.OrderItem('btc38','ltc')

    orderitem.buy_order_id = 1234
    orderitem.buy_status = 'open'
    orderitem.buy_price = 1.1222
    orderitem.buy_amount = 20
    orderitem.buy_units = 18
    orderitem.buy_date = common.get_curr_time_str()

    pricebuffer = priceupdate.PriceBuffer('btc38', save_log_flag=False)
    # priceitem = pricebuffer.getpriceitem('btc38', 'doge_cny')
    #
    # orderitem.priceitem = priceitem

    # saveorder(orderitem)
    # updateorder(orderitem)
    # delorder(orderitem)
    openordercount()



if __name__ == '__main__':
    pass
    test()
