import btc38.client

#test api transaction
key='47ae44f72c3a93dd33e6177142189071'
secret='f68d9ca86eb175d93d4f992642197b1c7ba555b0e9bb747d989f91ccc3cdeed1'
accountid=43237

btc38Client = btc38.client.Client(key,secret, accountid)

bal=btc38Client.getMyBalance()
print(bal['doge_balance'])
#提交订单1-buy,2-sell

#neworder=btc38Client.submitOrder(2,'cny',0.03,1000,'doge')
#neworder=tradeapi.placeOrder('doge_cny','sell',0.03,1000)
#print(neworder)