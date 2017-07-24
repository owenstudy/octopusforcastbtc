#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 7/24/17 1:14 PM

from sqlalchemy.orm import mapper, sessionmaker
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.sql.expression import Cast
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.mysql import \
    BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
    DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
    LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
    NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
    TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR
import cointrans

# 表的属性描述对象
metadata = MetaData()

# 从类OrderItem中自动来生成
# 调用方法
#       orderitem = OrderItem('btc38', 'doge')
#       orderitem.gen_table_class()
# 生成后调整类型, priceitem(1000)

orderitemTable = Table(
    "t_coin_trans", metadata,
    Column('trans_id', INT(11), primary_key=True),
    Column('sell_order_id', INTEGER),
    Column('sell_units', FLOAT),
    Column('buy_status', VARCHAR(100)),
    Column('coin', VARCHAR(100)),
    Column('sell_price', FLOAT),
    Column('buy_order_id', INTEGER),
    Column('buy_amount', FLOAT),
    Column('sell_amount', FLOAT),
    Column('sell_date', VARCHAR(100)),
    Column('sell_status', VARCHAR(100)),
    Column('buy_date', VARCHAR(100)),
    Column('buy_price', FLOAT),
    Column('buy_units', FLOAT),
    Column('priceitem', VARCHAR(1000)),
    Column('market', VARCHAR(100))
)

# 创建数据库连接,MySQLdb连接方式
mysql_db = create_engine('mysql+pymysql://root:Windows2000@127.0.0.1:3306/coins')
# 创建数据库连接，使用 mysql-connector-python连接方式
# mysql_db = create_engine("mysql+mysqlconnector://用户名:密码@ip:port/dbname")
# 生成表
metadata.create_all(mysql_db)


# 创建一个映射类
class Order(object):
    pass


# 把表映射到类
mapper(Order, orderitemTable)
# 创建了一个自定义了的 Session类
Session = sessionmaker()
# 将创建的数据库连接关联到这个session
Session.configure(bind=mysql_db)
session = Session()

# 保存一个新的order
def saveorder(orderitem):
    pass

# 更新一个order
def updateorder(orderitem):
    pass

# 得到OPEN 记录的数量
def openordercount():
    pass



import cointrans
if __name__ == '__main__':
    pass

