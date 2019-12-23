#coding:utf-8
import hmac
import hashlib
import requests
import sys
import time
import base64
import json
from collections import OrderedDict

class Fmex():
    def __init__(self,base_url = 'https://api.fmex.com/'):
        self.base_url = base_url

    def auth(self, key, secret):
        self.key = bytes(key,'utf-8') 
        self.secret = bytes(secret, 'utf-8')


    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.base_url + api_url
        for i in range(5):
            try:
                r = requests.request(method, r_url, params=payload)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
            if r.status_code == 200:
                return r.json()
            else:
                time.sleep(5)

    def get_signed(self, sig_str):
        """signed params use sha512"""
        # sig_str = base64.b64decode(bytes(sig_str))
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())
        return signature


    def signed_request(self, method, api_url, **payload):
        """request a signed url"""

        param=''
        if payload:
            sort_pay = sorted(payload.items())
            #sort_pay.sort()
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = str(int(time.time() * 1000))
        full_url = self.base_url + api_url

        if method == 'GET':
            if param:
                full_url = full_url + '?' +param
            sig_str = method + full_url + timestamp
        elif method == 'POST':
            sig_str = method + full_url + timestamp + param

        signature = self.get_signed(bytes(sig_str, 'utf-8'))

        headers = {
            'FC-ACCESS-KEY': self.key,
            'FC-ACCESS-SIGNATURE': signature,
            'FC-ACCESS-TIMESTAMP': timestamp

        }
        
        for i in range(5):
            try:
                r = requests.request(method, full_url, headers = headers, json=payload)
                r.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print(err)
                print(r.text)
                print(full_url)
                print(payload)
                print(headers)
                time.sleep(0.2)
            if r.status_code == 200:
                return r.json()
            elif r.status_code == 400:
                continue
                #return r.json() # {"status":3008,"msg":"submit cancel invalid order state"}
                                # {"status":1016,"msg":"account balance insufficient"}
            else:
                time.sleep(5)
                print(r.status_code)

    def get_contracts_symbols(self):
        """Get contracts symbols"""
        return self.public_request('GET','v2/public/contracts/symbols')['data']

    def get_server_time(self):
        """Get server time"""
        return self.public_request('GET','v2/public/server-time')['data']

    def get_contracts_currencies(self):
        """get contracts currencies"""
        return self.public_request('GET', 'v2/public/contracts/currencies')['data']

    def get_indexes_symbols(self):
        """get indexes symbols"""
        return self.public_request('GET', 'v2/public/indexes/symbols')['data']

    def get_market_ticker(self, symbol):
        """get market ticker"""
        return self.public_request('GET', 'v2/market/ticker/{symbol}'.format(symbol=symbol))

    def get_market_depth(self, level, symbol):
        """get market depth"""
        return self.public_request('GET', 'v2/market/depth/{level}/{symbol}'.format(level=level, symbol=symbol))

    def get_trades(self,symbol):
        """get detail trade"""
        return self.public_request('GET', 'v2/market/trades/{symbol}'.format(symbol=symbol))

    def get_candle(self,resolution,symbol):
        """get candle info"""
        return self.public_request('GET', 'v2/market/candles/{resolution}/{symbol}'.format(resolution=resolution,symbol=symbol))

    def get_candle_timestamp(self,resolution,symbol,before):
        """get candle info"""
        return self.public_request('GET', 'v2/market/candles/{resolution}/{symbol}?before={before}'.format(resolution=resolution,symbol=symbol,before=before))

    def get_market_indexes(self):
        """get market indexes"""
        return self.public_request('GET', 'v2/market/indexes')

    def get_market_fex(self):
        """get market fex"""
        return self.public_request('GET', 'v2/market/fex')

    def get_balance(self):
        """get user balance"""
        return self.signed_request('GET', 'v3/contracts/accounts')

    def get_trans_log(self):
        """get transfer logs"""
        return self.signed_request('GET', 'v3/contracts/transfer/logs')

    def create_order(self, **payload):
        """create order"""
        return self.signed_request('POST','v3/contracts/orders', **payload)

    def buy_limit_long(self,symbol, price, quantity):
        """buy someting"""
        return self.create_order(symbol=symbol, direction='LONG', type='LIMIT', price=str(price), quantity=quantity)

    def buy_post_only_limit_long(self,symbol, price, quantity):
        return self.create_order(symbol=symbol, direction='LONG', type='LIMIT', price=str(price), quantity=quantity, post_only='true')
    
    def sell_limit_short(self,symbol, price, quantity):
        """buy someting"""
        return self.create_order(symbol=symbol, direction='SHORT', type='LIMIT', price=str(price), quantity=quantity)

    def sell_post_only_limit_short(self,symbol, price, quantity):
        return self.create_order(symbol=symbol, direction='SHORT', type='LIMIT', price=str(price), quantity=quantity, post_only='true')

    def get_order(self,order_id):
        """get specfic order"""
        return self.signed_request('GET', 'v3/contracts/orders/{order_id}'.format(order_id=order_id))
        
    def get_order5(self,order_id):
        """get specfic order"""
        return self.signed_request('GET', 'v3/contracts/orders/{order_id}'.format(order_id=order_id))

    def get_order_open(self):
        """get order open"""
        return self.signed_request('GET', 'v3/contracts/orders/open')

    def cancel_order(self,order_id):
        """cancel specfic order"""
        return self.signed_request('POST', 'v3/contracts/orders/{order_id}/cancel'.format(order_id=order_id))
