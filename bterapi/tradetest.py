

from bterapi import common
from bterapi import keyhandler

from bterapi.trade import TradeAPI,OrderItem

#test

keyhdl=keyhandler.KeyHandler('apikey')
tradeapi=TradeAPI(keyhdl.keys[0],keyhdl)

#获取定单状态
orderitem=OrderItem(order_id=62845364)
orderstatus=tradeapi.getOrderStatus(62845364)
print('order:%d,status:%s,amount:%d,price%f'%(orderstatus.order_id,orderstatus.status,orderstatus.amount,orderstatus.rate))
#获取帐户余额
bal=tradeapi.getFunds()
print(bal)
#下订单
neworder=tradeapi.placeOrder('doge_cny','sell',0.03,1000)
print(neworder)

