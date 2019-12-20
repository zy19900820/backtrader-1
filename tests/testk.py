# -*- coding: utf-8; py-indent-offset:4 -*-
import datetime
import os.path
import sys
import time

import backtrader as bt
#from utils.dateintern import num2Time

class TestStrategy(bt.Strategy):
    params = (
        ('k', 5),
        )
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.dataopen = self.datas[0].open
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low
        self.buyorders = list()
        self.sellorders = list()

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.sellorders.append(self.sell(price=order.executed.price+50, exectype=bt.Order.Limit))
                #self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                pass#self.log('SELL EXECUTED, %.2f' % order.executed.price)
        elif order.status in [order.Canceled]:
            pass
            #self.log('Order Canceled')
        elif order.status in [order.Margin]:
            pass
            #self.log('Order Margin')
        elif order.status in [order.Rejected]:
            pass
            #self.log('Order Rejected')

    def next(self):
        #self.log('BUY CREATE, %.2f' % self.dataclose[0])
        orderlen = len(self.buyorders)
        if orderlen != 0:
            #上次订单未成交则取消
            buyorder = self.buyorders[orderlen - 1]
            if buyorder.status in [buyorder.Submitted, buyorder.Accepted]:
                self.cancel(buyorder)

        buyprice = self.dataclose[0] - (self.datahigh[-1] - self.datalow[-1]) * self.params.k / 10.0
        #self.order.append(self.buy())
        self.buyorders.append(self.buy(price=buyprice, exectype=bt.Order.Limit))
        #self.order = self.sell()
    
    def stop(self):
        self.log('k:%d ending value:%2.f' % (self.params.k, self.broker.getvalue()))
    
if __name__ == '__main__':
    cerebro = bt.Cerebro()

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, 'datas/fmexFourHour2019.txt')

    data = bt.feeds.FmexFinanceCSVData(
            dataname=datapath,
            fromdate=datetime.datetime(2019, 10, 26),
            todate=datetime.datetime(2019, 11, 28),
            reverse=False)

    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.FixedSize, stake=0.1)
    #cerebro.addstrategy(TestStrategy)
    strats = cerebro.optstrategy(
            TestStrategy,
            k=range(0, 10))
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=-0.00025)
    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #cerebro.plot()
