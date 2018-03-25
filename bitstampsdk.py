#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""
@author: xuanzhi
@file: bitstampsdk.py

@bit_company: bitstamp
"""
import requests
import json
import time
import hashlib
import hmac
import csv



BASE_API = 'https://www.bitstamp.net/api/v2'	#交易站的主api


TICKER_API = '%s/ticker'% BASE_API
DEPTH_API = '%s/order_book'% BASE_API
BALANCE_API = '%s/balance'% BASE_API
TRANSACTIONS_API = '%s/user_transactions'% BASE_API
CANCEL_API = '%s/cancel_order'% BASE_API
CANCEL_ALL_API ='%s/cancel_all_orders'% BASE_API
ORDER_STAUS_API = '%s/order_status'% BASE_API
OPEN_ORDERS_API = '%s/open_orders'% BASE_API


def get_nonce_time():                            #获取unix时间
	curr_stamp = time.time()
	return str(int(curr_stamp))


class Client_Bitstamp():	#创建一个bitstamp所有服务的类
	def __init__(self,access_key,secret_key,customer_id):
		self._public_key = access_key
		self._private_key = secret_key
		self._customer_id = customer_id

	def _http_get(self,url):
		req = requests.get(url).text
		resp = json.loads(req)
		return resp

	def _http_post(self,url,data):
		response = requests.post(url,data=data)
		try:
			resp = json.loads(response.text)
		except:
			resp = None
		return resp

	def get_signature(self):	#签名文件
		nonce = get_nonce_time()
		message = (nonce+self._customer_id+self._public_key).encode('utf-8')
		signature = hmac.new(self._private_key.encode('utf-8'),msg=message,digestmod=hashlib.sha256).hexdigest().upper()
		data = {}
		data['key'] = self._public_key
		data['signature'] = signature
		data['nonce'] = nonce
		return data

	def _get_ticker(self,symbol='btc_usd'):    #一天情况总览
		symbol = symbol.replace('_','')
		url = TICKER_API + '/' + symbol + '/'
		temp = self._http_get(url)
		ticker = {'last':temp['last'],'high':temp['high'],'low':temp['low'],'vol':temp['volume'],'buy':temp['bid'],'sell':temp['ask']}
		return ticker

	def _get_depth(self,symbol='btc_usd'):     #盘口挂单情况
		symbol = symbol.replace('_','')
		url = DEPTH_API + '/' + symbol + '/'
		temp = self._http_get(url)
		bids = temp['bids'][:5]    #挂盘买单20档
		asks = temp['asks'][:5]    #挂盘卖单20档
		depth = {'bids':bids,'asks':asks}
		new_order = {'bids':bids[0],'asks':asks[0]}    #最靠前的买单和卖单
		gap = float(new_order['bids'][0]) - float(new_order['asks'][0])	#买一与卖一的差价
		return depth,new_order,round(gap,2)

	def _balance(self,symbol=None):	#账户余额情况
		url = BALANCE_API + '/'
		data = self.get_signature()
		temp = self._http_post(url,data)
		available = {}
		balance = {}
		reserved ={}
		trade_fee = {}
		for key,value in temp.items():
			if key.endswith('available'):
				available[key.split('_')[0]] = value
			elif key.endswith('balance'):
				balance[key.split('_')[0]] = value
			elif key.endswith('reserved'):
				reserved[key.split('_')[0]] = value
			elif key.endswith('fee'):
				trade_fee[key.split('_')[0]] = value
		summary = {'balance':balance,'available':available,'reserved':reserved}
		return summary,trade_fee

	def _transaction(self,symbol='btc_usd'):		#历史交易记录
		symbol = symbol.replace('_','')
		url = TRANSACTIONS_API + '/' + symbol + '/'
		data = self.get_signature()
		data['offset'] = 0
		data['limit'] = 100
		data['sort'] = 'desc'
		temp = self._http_post(url,data)
		return temp

	def _cancel(self,order_id,symbol=None):		#取消特定挂单
		url = CANCEL_API +'/'
		data = self.get_signature()
		data['id'] = order_id
		try:
			temp = self._http_post(url,data)
		except:
			print('Wrong order id!')
		return temp

	def _cancel_all(self,order_id_list=None,symbol=None):		#取消所有挂单
		url = CANCEL_ALL_API + '/'
		data = self.get_signature()
		try:
			temp = self._http_post(url,data)
		except:
			print('NO opened orders!')
		return temp

	def _order_status(self,order_id,symbol=None):		#查询挂单信息
		url = ORDER_STAUS_API +'/'
		data = self.get_signature()
		data['id'] = order_id
		try:
			temp = self._http_post(url,data)
		except:
			print('Wrong order id!')
		return temp

	def _open_orders(self,symbol=None):		#所有活跃的挂单
		symbol = symbol.replace('_','')
		url = OPEN_ORDERS_API + '/' + symbol
		data = self.get_signature()
		temp = self._http_post(url,data)
		return temp

	def _trade(self,trade_type,amount,price,symbol=None):		#交易，limit_buy,market_buy,limit_sell,market_sell
		symbol = symbol.replace('_','')
		side,_type = trade_type.split('_')
		data = self.get_signature()
		data['amount'] = amount
		if _type == 'buy':
			if side == 'market':
				url = BASE_API + '/buy/market/' + symbol
				temp = self._http_post(url,data)
			elif side == 'limit':
				url = BASE_API + '/buy/' + symbol
				temp = self._http_post(url,data)
		elif _type == 'sell':
			if side == 'market':
				url = BASE_API + '/sell/market/' + symbol
				temp = self._http_post(url,data)
			elif side == 'limit':
				url = BASE_API + '/sell/' + symbol
				temp = self._http_post(url,data)
		return temp



access_key,secret_key,customer_id = input('a-key,s-key,c_id ').strip().split(',')
clien_bitstamp = Client_Bitstamp(access_key,secret_key,customer_id)
print(clien_bitstamp._get_ticker())
print(clien_bitstamp._balance())




