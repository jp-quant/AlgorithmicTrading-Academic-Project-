from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import matplotlib
import matplotlib.pyplot as plt
import os
import datetime
import json
from pprint import pprint
from mainframe import MainFrame
from portfolio import Portfolio


# stock will only pull at max 9 days of data if it's intraday
# other options will pull 20 years worth of data

session = MainFrame(api = '0GSGYX7YU9H0UHHZ',
                     market = 'stocks',
                     opy_start = '2018-1-01',
                     opy_end = '2018-1-05',
                     symbols = ['AAPL','CALD'],
                     interval = ['daily','15min'])





'''
session = MainFrame(api = '881d5063adb42278ec205e6fab28d843-6aa13e5d27cedb70d786712a8032bc29',
                     market = 'forex',
                     opy_start = '2018-1-01',
                     opy_end = '2018-1-05',
                     symbols = ['EUR_USD','USD_CAD'],
                     interval = ['M15','H4'])
'''
portfolio = Portfolio(balance = 1000)




trade_session = 'AAPL_15min'
x = session.dataframe[trade_session]
for i in range(len(x)):
    if x.loc[x.iloc[i].name,'5. volume'] % 2 == 0:
        session.buy_trig = True
        session.sell_Trig = False
    else:
        session.buy_trig = False
        session.sell_trig = True
    if session.buy_trig == True:
        print 'bought'
    elif session.sell_trig == True:
        print 'sold'
    else:
        print 'else'

