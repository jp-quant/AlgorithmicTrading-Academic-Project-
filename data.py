import os, os.path
import pandas as pd
import datetime
from abc import ABCMeta, abstractmethod
from event import MarketEvent

class DataFrame(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, N=1):
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
        for i in self.symbols:
            self.symbol_data[i] = pd.io.parsers.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i,
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            if indexes is None:
                indexes = self.symbol_data[i].index
            else:
                indexes.union(self.symbol_data[i].index)
            self.latest_symbol_data[i] = []

        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index = indexes, method = 'pad').iterrows()

    def get_new_bar(self,symbol):
        for i in self.symbol_data[symbol]:
            yield tuple([symbol, datetime.datetime.strptime(i[0], '%Y-%m-%d %H:%M:%S'),
                        i[1]['1. open'], i[1]['2. high'], i[1]['3. low'], i[1]['4. close'],i[1]['5. volume']])

    
