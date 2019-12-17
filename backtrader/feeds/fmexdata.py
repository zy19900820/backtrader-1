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
import io
import itertools

from ..utils.py3 import (urlopen, urlquote, ProxyHandler, build_opener,
                         install_opener)

import backtrader as bt
from .. import feed
from ..utils import date2num


class FmexFinanceCSVData(feed.CSVDataBase):
    '''
    Parses pre-downloaded Yahoo CSV Data Feeds (or locally generated if they
    comply to the Yahoo format)

    Specific parameters:

      - ``dataname``: The filename to parse or a file-like object

      - ``reverse`` (default: ``False``)

        It is assumed that locally stored files have already been reversed
        during the download process

    '''

    params = (
        ('reverse', False),
    )

    def start(self):
        super(FmexFinanceCSVData, self).start()

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

    def _loadline(self, linetokens):
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

        self.lines.datetime[0] = dtnum
        o = float(linetokens[next(i)])
        h = float(linetokens[next(i)])
        l = float(linetokens[next(i)])
        c = float(linetokens[next(i)])
        v = float(linetokens[next(i)])
        self.lines.openinterest[0] = 0.0


        self.lines.open[0] = o
        self.lines.high[0] = h
        self.lines.low[0] = l
        self.lines.close[0] = c
        self.lines.volume[0] = v

        return True


