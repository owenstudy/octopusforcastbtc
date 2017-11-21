apiconfig={"key":"", "secret":"",
     "accountid":, "baseurl":"http://api.aex.com/" }
# 基础的交易货币，可以是cny, btc,usd等
base_currency = {"basecurrcode":"btc"}

# 交易相关的参数
trans_config = {"database": {"username":"coin", "password":"Windows2000", "ip":"localhost", "port":3306, "dbname": "coins"},
 "transaction":{"TRANS_AMOUNT_PER_ORDER":0.001, "MAX_OPEN_ORDER_POOL":5, "SELL_PROFIT_RATE":0.04, "CANCEL_DURATION":1800,
 "COIN_MAX_RATE_IN_OPEN_ORDERS":0.35, "STOP_LOST_RATE":0.10},
 "coinlist":"ltc_btc,eth_btc,etc_btc,tmc_btc,bcc_btc"
 }
