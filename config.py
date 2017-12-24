apiconfig={"key":"", "secret":"",
     "accountid":, "baseurl":"http://api.aex.com/" }
# 基础的交易货币，可以是cny, btc,usd等
base_currency = {"basecurrcode":"btc"}

# 交易相关的参数
trans_config = {"database": {"username":"coin", "password":"Windows2000", "ip":"localhost", "port":3306, "dbname": "coins"},
 "transaction":{"TRANS_AMOUNT_PER_ORDER":0.0005, "MAX_OPEN_ORDER_POOL":13, "SELL_PROFIT_RATE":0.088, "CANCEL_DURATION":1800,
 "COIN_MAX_RATE_IN_OPEN_ORDERS":0.35, "STOP_LOST_RATE":0.2},
 "coinlist":"ltc_btc,eth_btc,etc_btc,tmc_btc,bcc_btc,bts_btc,nxt_btc,xrp_btc,ardr_btc,inf_btc,doge_btc,bcd_btc"
 }

# wex api config
wex_apiconfig = {"key":"", "secret":"",
     "accountid":409225, "baseurl":"http://api.aex.com/" }

# 监控价格的coin list
price_monitor_coin_list = {"coinlist":"ltc_btc,tmc_btc,eth_btc,bcx_btc,bcc_btc,xrp_btc,bcd_btc,bcx_btc,sbtc_btc,dash_btc,nxt_btc,inf_btc"}

# sms发送的配置信息
sms_auth = {"apikey":"", "signature":"【水果尝尝鲜】"}

# 固定投资策略
# @buy_freq, 以多少小时为频率买一次,单位为小时
regular_invest_param={"buy_freq":5, "buy_time":"10:00", "buy_amt":{'btc':0.0002,'bitcny':11}, 'buy_max_amt':{'btc':0.002,'bitcny':100}, "sell_profit_rate":0.15, "stop_lost_rate":0.3, "coin_list":"ltc_btc,eth_btc,bcx_btc,ltc_bitcny"}