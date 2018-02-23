from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.cryptocurrencies import CryptoCurrencies
from TechnicalIndicators import *
import matplotlib
import matplotlib.pyplot as plt
import os
import datetime
import json
import pandas as pd
import errno
import oandapy as opy


class Backtest:
    
    def __init__(self,
                 trade_session,
                 portfolio,
                 strategy):
        
        self.feed = feed
        self.portfolio = porfolio
        
        start(self)

    def start(self):
        for i in range(len(feed)):
            apply_strategy(i)
            if buy_trigg == True:
                buy()
            if sell_trigg == True:
                sell()
    def apply_strategy(feed):
        if sm 
