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
        ('fivemaperiod', 5),
        ('tenmaperiod', 10),
        ('thirtymaperiod', 30),
        ('rsimaperiod', 18),
        ('rsivalue', 36),
        )

    def __init__(self):
        self.datetime = self.datas[0].datetime
        self.high = self.datas[0].high
        self.low = self.datas[0].low
        self.average = (self.datas[0].open + self.datas[0].close +
                self.datas[0].high + self.datas[0].low) / 4
        #print(self.datas[0].datetime[0])
        self.pendingorder = None
        self.completeorder = list()
        self.completenum = 0

        self.sma5 = bt.indicators.SimpleMovingAverage(
                self.datas[0], period=self.params.fivemaperiod)
        self.sma10 = bt.indicators.SimpleMovingAverage(
                self.datas[0], period=self.params.tenmaperiod)
        self.sma30 = bt.indicators.SimpleMovingAverage(
                self.datas[0], period=self.params.thirtymaperiod)
        self.rsi = bt.indicators.RSI(
                    self.datas[0], period=self.params.rsimaperiod)

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
            """
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f,  rsi: %.2f' %
                    (order.executed.price,
                    self.rsi[-1]))

            elif order.issell():
                self.log('SELL EXECUTED, Price: %.2f, rsi: %.2f' %
                        (order.executed.price,
                        self.rsi[-1]))
            """
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
        #traceback.print_stack()
        #self.log('Close, %.2f' % self.dataclose[0])
        #判断这个挂单是否已成交 没成交则取消
        if self.pendingorder:
            self.cancel(self.pendingorder)
            self.pendingorder = None
        if self.sma5[-1] > self.sma10[-1] and self.sma10[-1] > self.sma30[-1] and self.rsi[-1] > 100 - self.p.rsivalue:
            #self.log('SELL CREATE, %.2f' % (self.high[-1] + 0.5))
            self.pendingorder = self.sell(price=self.high[-1] + 0.5, exectype=bt.Order.Limit)
        if self.sma5[-1] < self.sma10[-1] and self.sma10[-1] < self.sma30[-1] and self.rsi[-1] < self.p.rsivalue:
            #self.log('BUY CREATE, %.2f' % (self.low[-1] - 0.5))
            self.pendingorder = self.buy(price=self.low[-1] - 0.5 , exectype=bt.Order.Limit)

    def stop(self):
        self.log('completenum:%d  ending value:%2.f rsi:%.2f rsimaperiod:%d' % (self.completenum, self.broker.getvalue(), self.p.rsivalue, self.p.rsimaperiod))
        #name = "-rsivalue:" + str(self.p.rsivalue) + "-rsimaperiod:" + str(self.p.rsimaperiod)
        #drawPrice(self.completeorder, name)
        #drawPosition(self.completeorder, name)
        #drawValue(self.completeorder, name)

        #for i in range(len(self.completeorder)):
            #print(bt.num2date(self.completeorder[i].executed.dt))

if __name__ == '__main__':
    btotal = False
    cerebro = bt.Cerebro()
    cerebro.setbroker(bt.brokers.FmexBackBroker())

    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, '../datas/fmexOneMin2019.txt')

    data = bt.feeds.FmexFinanceCSVData(
            dataname=datapath,
            fromdate=datetime.datetime(2019, 12, 17),
            todate=datetime.datetime(2019, 12, 22),
            reverse=False)

    cerebro.adddata(data)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    if btotal:
        strats = cerebro.optstrategy(
                TestStrategy,
                rsivalue=range(10, 45),
                rsimaperiod=range(5, 45))
    else:
        cerebro.addstrategy(TestStrategy)
    cerebro.broker.setcash(1000000.0)
    cerebro.broker.setcommission(commission=-0.00025)
    #print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    cerebro.run()
    #print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    #cerebro.plot()
