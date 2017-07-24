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
)
