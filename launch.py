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


start = StartProgram(api = 'YOUR_API_KEY',
                     market = 'stocks',
                     opy_start = '2018-1-01',
                     opy_end = '2018-1-05',
                     symbols = ['AAPL','CALD'],
                     interval = ['15min'])


"""
start = StartProgram(api = 'YOUR_API_KEY',
                     market = 'forex',
                     opy_start = '2018-1-01',
                     opy_end = '2018-1-05',
                     symbols = ['EUR_USD','USD_CAD'],
                     interval = ['M15','M30','H4'])
"""
