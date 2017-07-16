#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Owen_Study/owen_study@126.com'
# Create date: 17-7-16 上午10:19

from priceupdate import PriceItem,PriceBuffer
import common
'''从价格文件中读取价格信息，进行对比研究，确定参数'''

class PriceStudy(object):
    def __init__(self,pricefilename = None):
        if pricefilename!=None:
            self.__pricefile=open(pricefilename,'r')
        else:
            self.__pricefile = open('pricehistory.log','r')
    def test(self):
        # pricebuffer = self.__read_price_list()
        testresult = self.simulate_verify_price()

        for resultitem in testresult:
            if float(resultitem.get('verify_correct_rate'))>0.2:
                print(resultitem)


    '''读取文件中的价格到price pricebuff'''
    def __read_price_list(self):
        # TODO 默认先读取全部，后面文件增大后需要分批处理
        pricebuffer = PriceBuffer(save_log_flag=False)
        firstline=True
        for priceline in self.__pricefile.readlines():
            if firstline is True:
                firstline = False
                continue
            priceitems=priceline.split('|')
            pricedate = common.CommonFunction.strtotime(priceitems[1].strip())
            pricecoin = priceitems[2].strip()
            price_buy = float(priceitems[3])
            price_buy_depth = float(priceitems[4])
            price_sell = float(priceitems[5])
            price_sell_depth = float(priceitems[6])

            priceitem = PriceItem(pricedate, pricecoin, price_buy, price_buy_depth, price_sell, price_sell_depth)
            pricebuffer.newprice(priceitem)
        return pricebuffer
    '''通过参数变更来校验结果'''
    def simulate_verify_price(self):
        # 取出当前文件中所有的价格进行多次运算验证
        basepricebuffer = self.__read_price_list()
        testresult=[]
        # 买入趋势的权重范围
        for price_trend_strong in range(6, 20):
            # 不买入权重的比例范围
            for price_trend_weak in range(4, 9):
                # 买入指数的变动范围
                for buy_index in range(5, 20):
                    testbuffer1 = PriceBuffer(save_log_flag=False)
                    testbuffer1.adjust_params(buy_index/10, price_trend_strong/10, price_trend_weak/10)
                    #testbuffer1.basetime=common.CommonFunction.strtotime('2017-07-16 01:08:19')
                    # 对价格列表用新的参数进行模拟
                    for priceitem in basepricebuffer.price_buffer:
                        testbuffer1.newprice(priceitem)
                    # TODO 判断当前参数的结果
                    forecast_correct_rate = self.get_verify_rate(testbuffer1)
                    each_test_result={'price_trend_strong_percentage': price_trend_strong/10, 'price_trend_weak_percentage': price_trend_weak/10,\
                                      'buy_index':buy_index/10, 'verify_correct_rate':forecast_correct_rate}
                    testresult.append(each_test_result)
        return testresult
    '''统计测试数据中验证通过的记录比例'''
    def get_verify_rate(self, pricebuffer):
        total_verify_correct_records = 0
        total_records=len(pricebuffer.price_buffer)
        total_forecast_records = 0
        for priceitem in pricebuffer.price_buffer:
            if priceitem.price_buy_forecast is True:
                total_forecast_records=total_forecast_records+1
                if priceitem.price_buy_forecast_verify is True:
                    total_verify_correct_records = total_verify_correct_records + 1
        if total_forecast_records == 0:
            correct_rate = 0
        else:
            correct_rate = round(total_verify_correct_records/total_forecast_records, 4)
        return correct_rate


if __name__ == '__main__':
    pricestudy = PriceStudy()
    pricestudy.test()
    pass