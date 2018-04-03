
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import TechnicalIndicators as ti
import matplotlib
import matplotlib.pyplot as plt
import json
import errno
import oandapy as opy

import os, os.path
import pandas as pd
import datetime
from abc import ABCMeta, abstractmethod
from event import MarketEvent

class DataFrame(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N):
        raise NotImplementedError('implement latest_bars() to proceed')

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError('implement update_bars() to proceed')

class HistoricalCSVData(DataFrame):
    def __init__(self, events, csv_path, symbols):
        self.events = events
        self.csv_path = csv_path
        self.symbols = symbols
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True
        
        self.load_csv()
            
    def update_bars(self):
        for i in self.symbols:
            try:
                bar = self.get_new_bar(i).next()
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[i].append(bar)
        self.events.put(MarketEvent())
            
    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            return 'Symbol is not available from historical data'
        else:
            return bars_list[-N:]
            
    def load_csv(self):
        indexes = None
        sma50_indexes = None
        sma100_indexes = None
        self.check_and_update(self.symbols)
        for i in self.symbols:
            self.symbol_data[i] = pd.io.parsers.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i,
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            self.symbol_data[str(i+'_sma50')] = pd.io.parsers.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i + '_sma50',
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            self.symbol_data[str(i+'_sma100')] = pd.io.parsers.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i + '_sma100',
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            if sma50_indexes is None:
                sma50_indexes = self.symbol_data[str(i+'_sma50')].index
            else:
                sma50_indexes.union(self.symbol_data[str(i+'_sma50')].index)
            if sma100_indexes is None:
                sma100_indexes = self.symbol_data[str(i+'_sma100')].index
            else:
                sma100_indexes.union(self.symbol_data[str(i+'_sma100')].index)
            if indexes is None:
                indexes = self.symbol_data[i].index
            else:
                indexes.union(self.symbol_data[i].index)
            self.latest_symbol_data[i] = []

        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index = indexes, method = 'pad').iterrows()
            self.symbol_data[str(i+'_sma50')] = self.symbol_data[str(i+'_sma50')].reindex(index = sma50_indexes, method = 'pad').iterrows()
            self.symbol_data[str(i+'_sma100')] = self.symbol_data[str(i+'_sma100')].reindex(index = sma100_indexes, method = 'pad').iterrows()

    def get_new_bar(self,symbol):
        o = None
        h = None
        l = None
        c = None
        v = None
        sma50 = None
        sma100 = None
        for i in self.symbol_data[symbol]:
            for sma50 in self.symbol_data[str(symbol + '_sma50')]:
                for sma100 in self.symbol_data[str(symbol + '_sma100')]:
                    ophl_indexes = i[1].axes
                    for x in ophl_indexes[0]:
                        if 'open' in x.lower():
                            o = x
                        if 'high' in x.lower():
                            h = x
                        if 'low' in x.lower():
                            l = x
                        if 'close' in x.lower():
                            c = x
                        if 'volume' in x.lower():
                            v = x
                    yield tuple([symbol, datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'),
                                i[1][o], i[1][h], i[1][l], i[1][c],i[1][v],
                                sma50[1]['SMA'], sma100[1]['SMA']])
                    '''yield tuple([symbol, datetime.datetime.strptime(i[0], '%Y-%m-%d'),
                                i[1][o], i[1][h], i[1][l], i[1][c],i[1][v],
                                sma50[1]['SMA'], sma100[1]['SMA']])'''

    def check_and_update(self,symbols, interval = '1min'):
        ts = TimeSeries(key='0GSGYX7YU50H0UHHZ', output_format = 'pandas')
        for i in symbols:
            check = os.path.exists(self.csv_path + '/' + i + '.csv')
            if check == True:
                print str(i) + '\'s data already exist and ready for backtest...'
            if check == False:
                print str(i) + '\'s data was not available'
                data = ts.get_intraday(symbol = i, interval = interval, outputsize = 'full')
                data[0].to_csv(self.csv_path + '/' + i + '.csv')
                sma50 = ti.sma(symbol = i, interval = interval, time_period = 50, series_type = 'close')
                sma100 = ti.sma(symbol = i, interval = interval, time_period = 100, series_type = 'close')
                sma50[0].to_csv(self.csv_path + '/' + i + '_sma50.csv')
                sma100[0].to_csv(self.csv_path + '/' + i + '_sma100.csv')
                print str(i) + '\'s data just got downloaded and ready for backtest...'
            
