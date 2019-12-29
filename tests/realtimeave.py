# -*- coding: utf-8; py-indent-offset:4 -*-
import datetime
import traceback
import os.path
import sys
import time

import testcommon
import backtrader as bt
#from utils.dateintern import num2Time

import matplotlib
matplotlib.use('Tkagg')
import matplotlib.pyplot as plt

def drawValue(trades, num):
    fig = plt.figure()

    timeStamp = []
    size = 0
    cash = 1000000
    values = []

    for i in range(len(trades)):
        #timeStamp.append(trades[i].entryTimeStamp_)
        timeStamp.append(bt.num2date(trades[i].executed.dt))
        size = size + trades[i].size
        cash = cash - trades[i].executed.price * trades[i].size
        value = cash + size * trades[i].executed.price
        #print(value)
        #print(trades[i].executed.price)
        #print(size)
        values.append(value)
    
    plt.plot(timeStamp, values)
    plt.gcf().autofmt_xdate()
    name = "pic/value" + str(num) + ".png"
    fig.savefig(name)
    plt.cla()
    plt.close("all")

def drawPosition(trades, num):
    fig = plt.figure()

    timeStamp = []
    position = []
    size = 0

    for i in range(len(trades)):
        #timeStamp.append(trades[i].entryTimeStamp_)
        timeStamp.append(bt.num2date(trades[i].executed.dt))
        size = size + trades[i].size
        position.append(size)
    
    plt.plot(timeStamp, position)
    plt.gcf().autofmt_xdate()
    name = "pic/position" + str(num) + ".png"
    fig.savefig(name)
    plt.cla()
    plt.close("all")

def drawPrice(trades, num):
    fig = plt.figure()

    timeStamp = []
    price = []

    for i in range(len(trades)):
        #timeStamp.append(datetime.fromtimestamp(trades[i].entryTimeStamp_))
        timeStamp.append(bt.num2date(trades[i].executed.dt))
        price.append(trades[i].price)
    
    plt.plot(timeStamp, price)
    plt.gcf().autofmt_xdate()
    name = "pic/price" + str(num) + ".png"
    fig.savefig(name)
    plt.cla()
    plt.close("all")

class TestStrategy(bt.Strategy):
    params = (
        ('maperiod', 56),
        )

    def __init__(self):
        self.bstart = False
        self.datetime = self.datas[0].datetime
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.average = (self.datas[0].open + self.datas[0].close +
                self.datas[0].high + self.datas[0].low) / 4
        #print(self.datas[0].datetime[0])
        self.pendingorder = None
        self.completeorder = list()
        self.completenum = 0

        self.sma = bt.indicators.SimpleMovingAverage(
                self.datas[0], period=self.params.maperiod)

    def log(self, txt, dt=None):
        dt = dt or bt.num2date(self.datetime[0])
        print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self.completenum = self.completenum + 1
            self.completeorder.append(order)
            self.pendingorder = None
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f' %
                    order.executed.price)

            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f' %
                        order.executed.price)

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
        if not self.bstart:
            return
        #traceback.print_stack()
        #self.log('Close, %.2f' % self.dataclose[0])
        #判断这个挂单是否已成交 没成交则取消
        if self.pendingorder:
            self.cancel(self.pendingorder)
            self.pendingorder = None
        if self.average[-1] > self.sma[-1]:
            self.log('SELL CREATE, %.2f' % (self.high[-1] + 0.5))
            self.pendingorder = self.sell(price=self.high[-1] + 0.5, exectype=bt.Order.Limit)
        if self.average[-1] < self.sma[-1]:
            self.log('BUY CREATE, %.2f' % (self.low[-1] + 0.5))
            self.pendingorder = self.buy(price=self.low[-1] + 0.5, exectype=bt.Order.Limit)

    def stop(self):
        self.log('completenum:%d maperiod:%d ending value:%2.f' % (self.completenum, self.params.maperiod, self.broker.getvalue()))
        drawPrice(self.completeorder, self.params.maperiod)
        drawPosition(self.completeorder, self.params.maperiod)
        drawValue(self.completeorder, self.params.maperiod)

        #for i in range(len(self.completeorder)):
            #print(bt.num2date(self.completeorder[i].executed.dt))

if __name__ == '__main__':
    btotal = False
    cerebro = bt.Cerebro()
    cerebro.setbroker(bt.brokers.FmexRealBroker())

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/fmexOneMin2019.txt')

    data = bt.feeds.FmexFinanceData(
            dataname=datapath,
            fromdate=datetime.datetime(2019, 12, 17),
            todate=datetime.datetime(2020, 12, 28),
            reverse=False)

    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    if btotal:
        strats = cerebro.optstrategy(
                TestStrategy,
                maperiod=range(2, 120))
    else:
        cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=0.000)
    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #cerebro.plot()
