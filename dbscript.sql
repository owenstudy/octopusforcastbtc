

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
buy_price FLOAT(10,5),
buy_units FLOAT(10,5),
buy_amount FLOAT(10,5),
buy_status VARCHAR(100),
sell_order_id INT,
sell_date VARCHAR(100),
sell_price FLOAT(10,5),
sell_units FLOAT(10,5),
sell_amount FLOAT(10,5),
sell_status VARCHAR(100),
priceitem VARCHAR(1000),
PRIMARY KEY (trans_id)
);

create table t_coin_trans_log as select * from t_coin_trans where 1=0;
