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
from scr import StartProgram
from sys import version_info 

py3 = version_info[0] > 2

if py3:
    user_market = input('Enter Market: (stocks, forex, etc)')
    if user_market == 'stocks':
        user_symbol = (input('Enter Asset Symbol: (AAPL, NFLX, etc)')).split(',')
        user_interval = (input('Enter Time Interval: (15min, 30min, 60min, daily, monthly)')).split(',')

        start = StartProgram(api = 'YOUR_API_KEY',
                     market = user_market,
                     opy_start = '2000-1-01',
                     opy_end = '2018-1-01',
                     symbols = user_symbol,
                     interval = user_interval)
else:
    user_market = raw_input('Enter Market: (stocks, forex, etc)')
    if user_market == 'stocks':
        user_symbol = (raw_input('Enter Asset Symbol: (AAPL, NFLX, etc)')).split(',')
        user_interval = (raw_input('Enter Time Interval: (15min, 30min, 60min, daily, monthly)')).split(',')

        start = StartProgram(api = 'YOUR_API_KEY',
                     market = user_market,
                     opy_start = '2000-1-01',
                     opy_end = '2018-1-01',
                     symbols = user_symbol,
                     interval = user_interval)


"""
start = StartProgram(api = 'YOUR_API_KEY',
                     market = 'forex',
                     opy_start = '2018-1-01',
                     opy_end = '2018-1-05',
                     symbols = ['EUR_USD','USD_CAD'],
                     interval = ['M15','M30','H4'])
"""
