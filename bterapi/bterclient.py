from bterapi import common
from bterapi import keyhandler
from bterapi.trade import TradeAPI,OrderItem
import openorderlist

#定义调用的客户端类，KEY和secrect在内部处理完成
class Client:
    def __init__(self, access_key=None, secret_key=None, account_id=None):
        keyinfo = keyhandler.KeyHandler('apikey')
        self.tradeapi = TradeAPI(keyinfo.keys[0], keyinfo)

    #提交定单，只需要传入参数就直接执行
    #('doge_cny','sell',0.03,1000)
    def submitOrder(self,pair, trade_type, rate, amount, connection=None, update_delay=None, error_handler=None):
        # 下订单
        neworder =self.tradeapi.placeOrder(pair,trade_type,rate,amount)
        return neworder
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        try:
            coinbal = None
            bal = self.tradeapi.getFunds()
            #coin, curr = pair.split("_")
            #print(bal[coin]['available'])
            if coin:
                try:
                    coinbal=bal[coin]['available']
                except:
                    coinbal=None

            else:
                # only 返回有值的列表#, 所有的都返回，把值转换成数字
                coin_list=list(bal.keys())
                for coin in coin_list:
                    #if float(bal[coin]['available'])>0:
                    bal[coin]['available']=float(bal[coin]['available'])
                    bal[coin]['locked'] = float(bal[coin]['locked'])
                    pass
                    #else:
                    #    del bal[coin]
                coinbal = bal
        except Exception as e:
            print(str(e))
            print('获取BTER余额异常！')
            pass
        return coinbal
    #得到open order list
    def getOpenOrderList(self,coin_code_pair):
        order_list=self.tradeapi.getOpenOrderList(coin_code_pair)
        open_order_list=[]
        for order in order_list:
            open_order_item = openorderlist.OpenOrderItem(order.order_id,'bter',coin_code_pair,order.type,\
                                                          float(order.rate),float(order.initial_amount),order.date)
            open_order_list.append(open_order_item)
        return open_order_list
        pass

    #得到某个order的状态
    def getOrderStatus(self,orderid,coin_code=None):
        except_times=0
        max_except_times=5
        return_order_status=None
        # If there is exception then continue to redo so that we can get correct order status
        while(except_times<max_except_times and return_order_status==None):
            try:
                orderstatus=self.tradeapi.getOrderStatus(orderid)
                # Only have two status, open or closed(including cancelled)
                if orderstatus.status!='open':
                    return_order_status='closed'
                else:
                    #部分成交的情况，认为是成功的，目前的接口不能保证部分成功的处理，只能默认为成功
                    if orderstatus.amount<orderstatus.initial_amount:
                        #return_order_status='partial_open'
                        return_order_status='closed'
                    else:
                        return_order_status = 'open'
            except:
                except_times=except_times+1
                print('bter: Get order status has %d errors happened!'%except_times)

        return return_order_status
    #取消定单, coincode just for format which is same for both markets
    def cancelOrder(self,orderid,coincode=None):
        cancelstatus= self.tradeapi.cancelOrder(orderid)
        if cancelstatus=='Success':
            format_cancelstatus='success'
        else:
            order_status=self.getOrderStatus(orderid,coincode)
            if order_status=='closed':
                format_cancelstatus='trans_done'
            else:
                format_cancelstatus='fail'
        return format_cancelstatus
    # get price
    def getPrice(self,coin_pair):
        pricedata=self.tradeapi.get_price(coin_pair)
        return pricedata
if __name__=='__main__':
    bterclient=Client()
    #获取帐户余额
    #bal=bterclient.getMyBalance('cny')

    #submitorder=bterclient.submitOrder('doge_cny','sell',0.03,100)
    #print(submitorder.order_id)
    #print(bal)

    price=bterclient.getPrice('doge_cny')

    # test order status
    submitorder = bterclient.submitOrder('doge_cny', 'sell', 0.01617, 100)
    submitorder2 = bterclient.submitOrder('doge_cny', 'buy', 0.01617, 200)
    order_status=bterclient.getOrderStatus(submitorder2.order_id,'doge')
    cancel_order=bterclient.cancelOrder(submitorder.order_id,'doge')
    #校验成交部分订单时的状态

    #测试get open order list
    open_order_list=bterclient.getOpenOrderList('doge_cny')
    for order in open_order_list:
        print(order.order_id)

