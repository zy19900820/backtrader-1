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
    print("drawValue start...")
    print("trades len:%d " % len(trades))
    print("num:%s " % str(num))
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
        print("i:%d" % i)
        print("total size:%.2f" % size)
        print("size:%.2f" % trades[i].size)
        print("cash:%.2f" % cash)
        print("value:%.2f" % value)
        values.append(value)
    
    plt.plot(timeStamp, values)
    plt.gcf().autofmt_xdate()
    name = ""
    if isinstance(num, int):
        name = "pic/value" + str(num) + ".png"
    else:
        name = "pic/value" + num + ".png"
    fig.savefig(name)
    plt.cla()
    plt.close("all")
    print("drawValue end...")

def drawPosition(trades, num):
    print("drawPosition start...")
    print("trades len:%d " % len(trades))
    print("num:%s " % str(num))
    fig = plt.figure()

    timeStamp = []
    position = []
    size = 0

    for i in range(len(trades)):
        #timeStamp.append(trades[i].entryTimeStamp_)
        timeStamp.append(bt.num2date(trades[i].executed.dt))
        size = size + trades[i].size
        print("i:%d" % i)
        print("total size:%.2f" % size)
        print("size:%.2f" % trades[i].size)
        position.append(size)
    
    plt.plot(timeStamp, position)
    plt.gcf().autofmt_xdate()
    name = ""
    if isinstance(num, int):
        name = "pic/position" + str(num) + ".png"
    else:
        name = "pic/position" + num + ".png"
    fig.savefig(name)
    plt.cla()
    plt.close("all")
    print("drawPosition end...")

def drawPrice(trades, num):
    print("drawPrice start...")
    print("trades len:%d " % len(trades))
    print("num:%s " % str(num))
    fig = plt.figure()

    timeStamp = []
    price = []

    for i in range(len(trades)):
        #timeStamp.append(datetime.fromtimestamp(trades[i].entryTimeStamp_))
        timeStamp.append(bt.num2date(trades[i].executed.dt))
        price.append(trades[i].price)
        print("i:%d" % i)
        print("price:%.2f" % trades[i].price)
    
    plt.plot(timeStamp, price)
    plt.gcf().autofmt_xdate()
    name = ""
    if isinstance(num, int):
        name = "pic/price" + str(num) + ".png"
    else:
        name = "pic/price" + num + ".png"
    fig.savefig(name)
    plt.cla()
    plt.close("all")
    print("drawPrice end...")

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
        self.d = {}
        self.drawstr = ""

        self.sma = bt.indicators.SimpleMovingAverage(
                self.datas[0], period=self.params.maperiod)

    def log(self, txt, dt=None):
        dt = dt or bt.num2date(self.datetime[0])
        print('%s, %s' % (dt.isoformat(), txt))

    def add_order(self, order):
        dt = bt.num2date(self.datetime[0])
        dtstr = dt.isoformat()[0:13]
        if dtstr in self.d:
            #dict 存在k 则加入订单
            self.d[dtstr].append(order)
        else:
            if self.drawstr != "":
            #不是第一次创建 则把上次的list打印出来 加入这次的list
                drawPrice(self.d[self.drawstr], self.drawstr)
                drawPosition(self.d[self.drawstr], self.drawstr)
                drawValue(self.d[self.drawstr], self.drawstr)

            self.drawstr = dtstr
            self.d[dtstr] = list()
            self.d[dtstr].append(order)
                

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            self.add_order(order)
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
            self.log('BUY CREATE, %.2f' % (self.low[-1] - 0.5))
            self.pendingorder = self.buy(price=self.low[-1] - 0.5, exectype=bt.Order.Limit)

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
