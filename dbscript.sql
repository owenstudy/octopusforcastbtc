

# create database
create database coins;

#create user name to access coins
create user coin identified by 'Windows2000';
#grant privileges to coin
    GRANT ALL PRIVILEGES ON coins.* TO 'coin' IDENTIFIED BY 'Windows2000';

    #change to coins database
    use coins;
    #create the transaction table to save the data
    CREATE TABLE IF NOT EXISTS t_coin_trans (
    trans_id INT(11) NOT NULL AUTO_INCREMENT,
    market VARCHAR(100),
    buy_order_id INT,
    buy_date VARCHAR(100),
    coin VARCHAR(100),
    buy_price FLOAT(14,10),
    buy_units FLOAT(14,10),
    buy_amount FLOAT(14,10),
    buy_status VARCHAR(100),
    sell_order_id INT,
    sell_date VARCHAR(100),
    sell_price FLOAT(14,10),
    sell_units FLOAT(14,10),
    sell_amount FLOAT(14,10),
    sell_status VARCHAR(100),
    priceitem VARCHAR(1000),
    PRIMARY KEY (trans_id)
    );
    # 交易历史
    create table t_coin_trans_log as select * from t_coin_trans where 1=0;

    # 从网01站查询的交易数据历史
    CREATE TABLE IF NOT EXISTS t_aex_trans (
    trans_id INT(11) NOT NULL AUTO_INCREMENT,
    id int(11),
    coin  VARCHAR(100),
    price FLOAT(14,10),
    volume FLOAT(18,10),
    btcvolume FLOAT(18,10),
    trans_time VARCHAR(100),
    buyer_id VARCHAR(100),
    seller_id VARCHAR(100),
    PRIMARY KEY (trans_id)
    );

    drop view v_profit_summary;
    create view v_profit_summary as
    select date_format(str_to_date(sell_date,'%Y-%m-%d %H:%i:%s'),'%Y-%m-%d') sellDate,sum(round((sell_amount-buy_amount)*2/3,10)) total_profit_amount, count(*) total_trans_count from t_coin_trans_log where sell_status='closed'
    group by date_format(str_to_date(sell_date,'%Y-%m-%d %H:%i:%s'),'%Y-%m-%d');

    # aex 网站的实际交易记录盈利情况
    drop view v_aex_profit_details;
    create view v_aex_profit_details as
    select coin, trans_time, btcvolume, 'sell' trans_type from t_aex_trans where seller_id<>0
    union all
    select coin, trans_time, btcvolume*-1 as btcvolume, 'buy' trans_type from t_aex_trans where buyer_id<>0
    union all
    select coin,sell_date as trans_time, sell_amount, 'sell' trans_type from t_coin_trans;

    # aex 的盈利明细
    drop view v_aex_profit_summary;
    create view v_aex_profit_summary as
    select coin,sum(btcvolume) profit_amount from v_aex_profit_details group by coin;

    drop view v_profit_all;
    create view v_profit_all as    select * from (

    select 'coins' as coins, a.* from coins.v_profit_summary a union
    select 'coins1' as coins, a.* from coins1.v_profit_summary a union
    select 'coins2' as coins, a.* from coins2.v_profit_summary a union
    select 'coins3' as coins, a.* from coins3.v_profit_summary a
    ) aa order by aa.selldate, aa.coins;

    create view v_trans_summary as
    select '交易中' trans_status, count(*) from t_coin_trans
    union
    select '交易完成' trans_status, count(*) from t_coin_trans_log where sell_status='closed'
    union
    select '买入取消' trans_status, count(*) from t_coin_trans_log where buy_status='cancelled'
    union
    select '卖出取消' trans_status, count(*) from t_coin_trans_log where sell_status='cancelled'
    ;

    drop view v_trans_all;
    create view v_trans_all as
    select 'coins', a.* from coins.v_trans_summary a union
    select 'coins1', a.* from coins1.v_trans_summary a union
    select 'coins2', a.* from coins2.v_trans_summary a union
    select 'coins3', a.* from coins3.v_trans_summary a

    ;

    drop view v_coin_trans_all;
    create view v_coin_trans_all as
    select 'coins', a.* from coins.t_coin_trans a union
    select 'coins1', a.* from coins1.t_coin_trans a union
    select 'coins2', a.* from coins2.t_coin_trans a union
    select 'coins3', a.* from coins3.t_coin_trans a
    ;

    drop view v_coin_trans_log_all;
    create view v_coin_trans_log_all as
    select 'coins' , a.* from coins.t_coin_trans_log a union
    select 'coins1' , a.* from coins1.t_coin_trans_log a union
    select 'coins2' , a.* from coins2.t_coin_trans_log a union
    select 'coins3' , a.* from coins3.t_coin_trans_log a
    ;

