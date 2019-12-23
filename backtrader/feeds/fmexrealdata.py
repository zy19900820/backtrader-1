#!/usr/bin/env python
# -*- coding: utf-8; py-indent-offset:4 -*-
###############################################################################
#
# Copyright (C) 2015, 2016, 2017 Daniel Rodriguez
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import collections
from datetime import date, datetime, time
from time import localtime, strftime, sleep
import io
import itertools

from ..utils.py3 import (urlopen, urlquote, ProxyHandler, build_opener,
                         install_opener)

import backtrader as bt
from .. import feed
from ..utils import date2num
from .. import fmex


class FmexFinanceData(feed.CSVDataBase):
    '''
    Parses pre-downloaded Yahoo CSV Data Feeds (or locally generated if they
    comply to the Yahoo format)

    Specific parameters:

      - ``dataname``: The filename to parse or a file-like object

      - ``reverse`` (default: ``False``)

        It is assumed that locally stored files have already been reversed
        during the download process

    '''
    fmexinterface = fmex.Fmex()

    params = (
        ('reverse', False),
        #('nowtime', 1577089380),
        ('nowtime', 1577108400),
    )

    def start(self):
        super(FmexFinanceData, self).start()

        if not self.params.reverse:
            return

        # Yahoo sends data in reverse order and the file is still unreversed
        dq = collections.deque()
        for line in self.f:
            dq.appendleft(line)

        f = io.StringIO(newline=None)
        f.writelines(dq)
        f.seek(0)
        self.f.close()
        self.f = f

    def _load(self):
        #填充最后一个array数据
        ret = self._loadline()
        return ret

    def _loadline(self):
    #def _loadline(self, linetokens):
        """
        while True:
            nullseen = False
            for tok in linetokens[1:]:
                if tok == 'null':
                    nullseen = True
                    linetokens = self._getnextline()  # refetch tokens
                    if not linetokens:
                        return False  # cannot fetch, go away

                    # out of for to carry on wiwth while True logic
                    break

            if not nullseen:
                break  # can proceed

        i = itertools.count(0)

        dttxt = linetokens[next(i)]
        dt = date(int(dttxt[0:4]), int(dttxt[5:7]), int(dttxt[8:10]))
        strTime = linetokens[next(i)]
        #dtTime = datetime.strptime(strTime, "%H:%M:%S")
        dtTime = time(int(strTime[0:2]), int(strTime[3:5]), int(strTime[6:8]), 0)
        #dtTime = datetime.time(1,1,1)
        dtnum = date2num(datetime.combine(dt, dtTime))

        o = float(linetokens[next(i)])
        h = float(linetokens[next(i)])
        l = float(linetokens[next(i)])
        c = float(linetokens[next(i)])
        v = float(linetokens[next(i)])

        self.lines.openinterest[0] = 0.0
        self.lines.datetime[0] = dtnum
        self.lines.open[0] = o
        self.lines.high[0] = h
        self.lines.low[0] = l
        self.lines.close[0] = c
        self.lines.volume[0] = v
        return True
        """
        candledata = self.fmexinterface.get_candle_timestamp("M1", "btcusd_p", self.p.nowtime)["data"]
        for i in range(len(candledata)):
            if self.p.nowtime <= candledata[i]["id"]:
                timeArray = localtime(candledata[i]["id"])
                timeStr = strftime("%Y-%m-%d %H:%M:%S", timeArray)
                print(timeStr)
                dt = date(int(timeStr[0:4]), int(timeStr[5:7]), int(timeStr[8:10]))
                dtTime = time(int(timeStr[11:13]), int(timeStr[14:16]), int(timeStr[17:19]), 0)
                dtnum = date2num(datetime.combine(dt, dtTime))
                print(dtnum)
                self.lines.datetime[0] = dtnum

                self.lines.open[0] = candledata[i]["open"]
                self.lines.close[0] = candledata[i]["close"]
                self.lines.high[0] = candledata[i]["high"]
                self.lines.low[0] = candledata[i]["low"]
                self.lines.volume[0] = candledata[i]["quote_vol"]
                self.p.nowtime = candledata[i]["id"] + 60
                return True

        return False


    def loadrealtime(self):
        print("loadreadtimestart")
        while 1:
            candledata = self.fmexinterface.get_candle_timestamp("M1", "btcusd_p", self.p.nowtime)["data"]
            for i in range(len(candledata)):
                if self.p.nowtime <= candledata[i]["id"]:
                    timeArray = localtime(candledata[i]["id"])
                    timeStr = strftime("%Y-%m-%d %H:%M:%S", timeArray)
                    print(timeStr)
                    dt = date(int(timeStr[0:4]), int(timeStr[5:7]), int(timeStr[8:10]))
                    dtTime = time(int(timeStr[11:13]), int(timeStr[14:16]), int(timeStr[17:19]), 0)
                    dtnum = date2num(datetime.combine(dt, dtTime))
                    print(dtnum)
                    self.lines.datetime[0] = dtnum

                    self.lines.open[0] = candledata[i]["open"]
                    self.lines.close[0] = candledata[i]["close"]
                    self.lines.high[0] = candledata[i]["high"]
                    self.lines.low[0] = candledata[i]["low"]
                    self.lines.volume[0] = candledata[i]["quote_vol"]
                    self.p.nowtime = candledata[i]["id"] + 60
                    return True
            
            print("now:%d\n" % self.p.nowtime)
            print("id:%d \n" % candledata[0]["id"])
            sleep(10)

        print("loadreadtimestart")
        return True
