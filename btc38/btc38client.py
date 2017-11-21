# -*- coding: UTF-8 -*-
import btc38.client
import urlaccess
import json,time,datetime
import openorderlist
from btc38.config import apiconfig
from btc38.config import base_currency
import pricemanage

'''统一接口'''
#test api transaction
key=apiconfig.get("key")
secret=apiconfig.get("secret")
accountid=apiconfig.get("accountid")


class Client():
    def __init__(self):
        #获取API信息
        self.btc38clt = btc38.client.Client(key, secret, accountid)
        # 基础的交易货币
        self.basecurrcode = base_currency.get('basecurrcode','btc')

        pass

    #提交定单，只需要传入参数就直接执行
    #('doge_cny','sell',0.03,1000)
    # 注意小数点的位数，太长的小数点会导致提交错误
    def submitOrder(self,pair, trade_type, rate, amount, connection=None, update_delay=None, error_handler=None):
        #btc38Client.submitOrder(2, 'cny', 0.03, 1000, 'doge')
        if trade_type=='sell':
            transtype=2
        else:
            transtype=1
        coin,curr=pair.split('_')
        order=self.btc38clt.submitOrder(transtype,curr,rate,amount,coin)
        #return format b'[succ|123423]
        order2=order[0].decode('utf8').split('|')
        #避免直接成交没有 返回订单的情况
        #orderstatus = order2[0]
        if order2[0]=='succ':
            orderstatus='success'
        else:
            orderstatus='fail'
        if len(order2)>=2:
            orderid=order2[1]
        else:
            print('注意没有返回订单号，使用虚拟号代码，有可能发生错误')
            if orderstatus=='success':
                #虚拟一个订单号,直接成功的订单，没有 返回定单号则给一个虚拟的订单号
                orderid = 1111111
            else:
                orderid = -1111111

        neworder={'order_id':orderid,'status':orderstatus}
        #转换成对象以方便 统一访问
        neworder2=urlaccess.JSONObject(neworder)
        return neworder2
    #得到某个COIN或者全部的余额信息
    #pair e.g. doge_cny
    def getMyBalance(self,coin=None):
        try:
            coinbal=None
            bal=self.btc38clt.getMyBalance()
            if coin:
                coinbal=float(bal[coin+'_balance'])
            else:
                # 统一格式，风格统一{'doge'：{available:22,locked:2234}},{...}
                coin_list=[]
                for coin in bal.keys():
                    coin_list.append(coin.split('_')[0])
                coin_list=list(set(coin_list))
                all_balance={}
                for coin in coin_list:
                    coin_balance=float(bal.get(coin+'_balance'))
                    coin_balance_lock=float(bal.get(coin+'_balance_lock'))
                    #if coin_balance>0:
                    all_balance[coin]={'available':coin_balance,'locked':coin_balance_lock}
                #print(all_balance)
                return all_balance
        except Exception as e:
            print(str(e))
            if str(e).find('line 1 column 8 (char 7)')>0:
                print('检查IP地址是不是加入了白名单！')
        return coinbal
    #取消定单,btc38传送时需要 放一个coin code否则为报错
    def cancelOrder(self,orderid,coin_code=None):
        try:
            order_status=None
            cancel=self.btc38clt.cancelOrder(coin_code,'btc',orderid)
            cancelstatus=cancel[0].decode('utf8')
            if cancelstatus=='succ':
                order_status='success'
            #the order has done before cancel
            elif cancelstatus=='no_record':
                order_status='trans_done'
            else:
                order_status = 'fail'
        except Exception as e:
            print(str(e))
            print('订单取消失败@btc38')
            order_status='fail'
        finally:
            return order_status

    # 得到open order list
    def getOpenOrderList(self, coin_code_pair):
        coin_code=coin_code_pair.split('_')[0]
        order_list = self.btc38clt.getOrderList(coin_code)
        open_order_list = []
        for order in order_list:
            if order.get('type')=='1':
                trans_type='buy'
            else:
                trans_type='sell'
            open_order_item = openorderlist.OpenOrderItem(order.get('id'), 'btc38', coin_code_pair, trans_type, \
                                                          float(order.get('price')), float(order.get('amount')), order.get('time'))
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
                data = self.btc38clt.getOrderList(coin_code)
                for order in data:
                    # 查找到有订单则说明没有 成交，是open状态，其它为closed，cancel也认为是closed
                    if int(order.get('id')) == int(orderid):
                        return_order_status='open'
                        break
                # Default to closed if cannot find in the open list
                if return_order_status==None:
                    return_order_status='closed'
            except:
                except_times=except_times+1
                print('btc38: Get order status has %d errors happened!' % except_times)

        return return_order_status

    #取得订单状态
    def getOrderStatusX(self,orderid,coin_code=None):
        #

        try:
            data=self.btc38clt.getOrderList(coin_code)
            #orderstatus=b'[{"order_id":"123", "order_type":"1", "order_coinname":"BTC", "order_amount":"23.232323", "order_price":"0.2929"}, {"order_id":"123", "order_type":"1", "order_coinname":"LTC","order_amount":"23.232323", "order_price":"0.2929"}]'
            #TODO 需要找出指定订单的状态
            orderresult=None
            order_status=None
            for order in data:
                #查找到有订单则说明没有 成交，是open状态，其它为closed，cancel也认为是closed
                if int(order.get('id'))==int(orderid):
                    orderresult={'order_id':orderid,'order_status':'open'}
                    break
            if not orderresult:
                orderresult = {'order_id': orderid, 'order_status': 'closed'}
            orderresultobj=urlaccess.JSONObject(orderresult)
            order_status=orderresultobj.order_status
        except Exception as e:
            #如果订单状态返回出错，则返回一个默认值
            print('获取订单状态出错')
            print(str(e))
            order_status='open'
        finally:
            return order_status
    '''得到市场的深度'''
    def getMarketDepth(self,coin_code,mk_type='btc'):
        try:
            data = self.btc38clt.getDepth(mk_type,coin_code)
            # 买单列表
            buylist=list(data.get('bids'))
            # 卖单列表
            selllist=list(data.get('asks'))

            depthlist=urlaccess.JSONObject({'date':datetime.datetime.now(),'sell':selllist,'buy':buylist})
        except Exception as e:
            print(str(e))
            depthlist= None
        return depthlist
    # 取得价格信息
    def getPrice(self,coin_pair):
        price=self.btc38clt.getTickers(coin_pair.split('_')[1],coin_pair.split('_')[0])
        priceobj = urlaccess.JSONObject(price)
        return priceobj
    # 获取交易的历史记录
    def getMyTradeList(self,coin_code):

        lastpage = False
        currpage = 0
        all_trans_list = []
        # 循环取出所有的交易历史记录，先是全部遍历，等记录过多时再进行额外处理
        while lastpage is not True:
            trade_list = self.btc38clt.getMyTradeList(self.basecurrcode,coin_code,currpage)
            if len(trade_list) != 0:
                all_trans_list.extend(trade_list)
                currpage = currpage +1
            else:
                lastpage = True
        # for trad        eitem in trade_list:
        #     pass
        #     print("{0}".format(tradeitem))

        return all_trans_list

if __name__=='__main__':
    client = Client()

    # price = client.getPrice('ltc_btc')
    depth = client.getMarketDepth('ltc_btc','btc')
    trade_list = client.getMyTradeList('eth')
    # print("My trade list:{0}".format(trade_list))
#     #submit=client.submitOrder('doge_cny','sell',0.03,100)
#     #print(submit.order_id)
#     #clt = client.getOrderStatus(367892140)
#     #print(clt)
#         #test open order list
#     open_order_list=client.getOpenOrderList('bcc_btc')
#     for order in open_order_list:
#         print('order_id:%s,trans_type:%s,trans_unit:%f'%(order.order_id,order.trans_type,float(order.trans_unit)))
#
#
#     btc38clt=Client()
#     """
#     bal=btc38clt.getMyBalance('doge')
#     print(bal)
#     neworder=btc38clt.submitOrder('doge_cny','sell',0.03,2000)
#     print(neworder)
#     bal=btc38clt.getMyBalance('doge')
#     print(bal)
#     cancel=btc38clt.cancelOrder(367711369)
#     print(cancel)
# """
#     #测试市场尝试
#     market_depht=btc38clt.getMarketDepth('doge','btc')
#     for buy in market_depht.buy:
#         print(buy)
#
#     order = btc38clt.submitOrder('doge_btc', 'sell', 0.01616, 100)
#     order_id=order.order_id
#     # order2=btc38clt.submitOrder('doge_btc', 'buy', 0.01616, 100)
#     # order_status=btc38clt.getOrderStatus(order2.order_id,'doge')
#     cancel_order=btc38clt.cancelOrder(order.order_id,'doge')
#
#     bal=btc38clt.getMyBalance('doge')
#     print(bal)

