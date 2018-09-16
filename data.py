
from alpha_vantage.foreignexchange import ForeignExchange
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
from alpha_vantage.sectorperformance import SectorPerformances
from alpha_vantage.cryptocurrencies import CryptoCurrencies
import matplotlib.pyplot as plt
import json
import errno
import statsmodels.api as sm #HPFilter
from statsmodels.tsa.seasonal import seasonal_decompose #ETS
from statsmodels.tsa.stattools import adfuller #unit root test for stationarity

import os, os.path
import pandas as pd
import numpy as np
import datetime
import time
from abc import ABCMeta, abstractmethod
from event import MarketEvent

##---- DATA STRUCTURE ------
##TIMESTAMP = PANDAS INDEXES FORMAT AS FOR MULTIPLE PURPOSES IN TRACKING EVENTS
##SYMBOL_DATA = DICTIONARY FORMAT, INDEX = SYMBOL
##                DATA = PANDAS DATAFRAME UPLOADED WHEN BEING INITIALIZED
##                THIS DATA FRAME IS INDEXED BY THE TIMESTAMP EXTRACTED WHEN WE INITIZLIED THE DATAFRAME
##LATEST_SYMBOL_DATA = SAME AS SYMBOL_DATA BUT THIS IS FOR EVENT DRIVEN PURPOSES
##                    DATA = LIST OF SERIES
##                    EACH SERIES = BAR DATA WITH ITS NAME AS STAMP
##
##IMPORTANT------
##---->>> DATA.PY AND STRATEGY.PY ARE THEIR OWN SECTOR.
##---->>> THEREFORE IT'S ESSENTIAL FOR YOU TO UNDERSTAND HOW DATA IS BEING PROCESSED
##---->>> SO YOU CAN CREATE YOUR OWN STRATEGY, AS TO HOW YOU WOULD HANDLE THEM
##---->>>>>>>>>---->>> MAIN POINT--> EVERY TIME YOU CALL THE ABSTRACT METHOD  
##                                    GET_LATEST_BARS, YOU WILL RECEIVE
##                                    A LIST OF SERIES AS BARS, EX: [BAR1, BAR2], FORMAT EXPLAINED ABOVE
##                                    YOU WILL THEN HANDLE THE DATA YOU HAVE DESIGNATED TO RECEIVE
##                                    TO PERFORM YOUR CALCULATIONS, THEN PUT THE SIGNAL NEEDED IN TO EVENT QUEUE
##




class DataFrame(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    #use in other components to obtain latest bars
    def get_latest_bars(self, symbol, N):
        raise NotImplementedError('implement latest_bars() to proceed')

    @abstractmethod
    #used in backtest.py to constantly update bars
    def update_bars(self):
        raise NotImplementedError('implement update_bars() to proceed')
    
    @abstractmethod
    #use to add additional data to the dataframe
    def add_data(self,symbols,periods,sma,ewma,cumreturns,hpfilter):
        raise NotImplementedError('implement add_sma to proceed') 

    # add more abstract methods if needed 

class CSVData(DataFrame):
    def __init__(self, events, csv_path, symbols):
        self.events = events
        self.csv_path = csv_path
        self.symbols = symbols
        self.symbol_data = {}
        self.timestamp = None #timestamp will be set after load.csv() is run
        self.latest_stamps = [] #use to track our timeindex, mostly for portfolio allocations optimizations
        self.latest_symbol_data = {}
        self.continue_backtest = True
        # After initializing all variables, we load all symbols' csv files (OHLCV) into symbol_data as generators
        self.load_csv()
            
    def update_bars(self,stop_at=None):
        #before updating bars, we need to grab the next timestamp and delete it from our existing ones
        try:
            stamp = self.timestamp[0]
            self.latest_stamps.append(stamp)
            self.timestamp = self.timestamp.drop(stamp)
            for i in self.symbols:
                bar = self.get_new_bar(i,stamp)
                if bar is not None:
                    self.latest_symbol_data[i].append(bar)
            self.events.put(MarketEvent(stamp)) #FIRST START, IMPORTANT
            if stop_at == None:
                pass
            else:
                if stamp == stop_at:
                    self.continue_backtest = False
                    print('As instructed, backtest stops at:',str(stop_at))
        except IndexError:
            self.continue_backtest = False
            print('BACKTEST COMPLETE.')
            
    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            return 'Symbol is not available from historical data'
        else:
            if N == 0: #N = 0 is set to return ALL bars updated on the dataframe
                return bars_list
            elif N < 0:
                print('N needs to be an integer >= 0')
            elif N > 0:
                return bars_list[-N:]
            
    def load_csv(self):
        #IMPORTANT: THE ORIGINAL DATA VETTED IN CHECK_AND_UPDATE
        #           NEED TO BE FIXED TO ['open','high','low','close','volume']
        indexes = None
        columns = ['open','high','low','close','volume']
        not_seen = []
        for i in self.symbols:
            path_check = os.path.exists(self.csv_path+'/'+i+'.csv')
            if path_check == True:
                pass
            elif path_check == False:
                not_seen.append(i)
        if len(not_seen) == 0:
            print('Data available for all symbols')
        else:
            print('Database is missing data for the following symbol(s): ')
            for i in not_seen:
                print(i)
            print('Backtest cannot start with missing data')
            print('Y = perform update process (might take a minute or two)')
            print('N = drop missing symbol data(s) and proceed')
        if len(not_seen) == 0:
            db_check = input('Wanna check and update database for potential new data? (Y/N): ')
        else:
            db_check = input('Wanna check and update database,? (Y/N): ')
        if str(db_check).lower() == 'y':
            self.check_and_update(symbols=self.symbols)
        else:
            print('Dataframe launched with pre-existing data')
        for i in self.symbols:
            self.symbol_data[i] = pd.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i,
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            
            self.symbol_data[i].columns = columns # clean up columns
            self.symbol_data[i] = self.symbol_data[i].sort_index() #sort index to make sure it's monotonic
            #self.symbol_data[i] = self.symbol_data[i].set_index(pd.to_datetime(self.symbol_data[i].index)) #set index to datetime
            if indexes is None:
                indexes = self.symbol_data[i].index
            else:
                indexes.union(self.symbol_data[i].index)
            self.latest_symbol_data[i] = [] #set latest symbol data in to a list to be appended later
        self.timestamp = indexes
        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index=indexes,method='pad')
        
    
    def get_new_bar(self,symbol,stamp):
        csv_data = self.symbol_data[symbol]
        new_bar = csv_data.loc[stamp] #bar contains informations, with its name = stamp
        return new_bar #return a pandas series to be appended to latest_symbol_data

    def check_and_update(self,symbols, interval = '1min'):
        api_keys = ['0GSGYX7YU9H0UHHZ','7ZL6EROSN2W13QP3']
        api = 0 #this represents the index of the current api key used
        for i in symbols:
            check = os.path.exists(self.csv_path+'/'+i+'.csv')
            if check == True: #if data file exists
                csv_data = pd.read_csv(os.path.join(self.csv_path,
                                                '{file_name}.{file_extension}'.format(file_name = i,
                                                file_extension = 'csv')),header = 0, index_col = 0)
                if (((datetime.date.today().day) > (datetime.datetime.strptime(csv_data.index[-1],'%Y-%m-%d %H:%M:%S').day)) or ((datetime.date.today().month) > (datetime.datetime.strptime(csv_data.index[-1], '%Y-%m-%d %H:%M:%S').month))) and (datetime.date.today().weekday() < 5):
                    # if today's day or month is later/more than csv's latest day or month (respectively)
                    # AND that today isn't Saturday or Sunday
                    # we will download new data and update
                    new = None
                    print(i+ '\'s ' + 'OHLCV data is outdated. Updating...')
                    while type(new) != pd.DataFrame:
                        try:
                            ts = TimeSeries(key=api_keys[api], output_format = 'pandas')
                            new = ts.get_intraday(symbol = i, interval = interval, outputsize = 'full')[0]
                        except ValueError:
                            print('API Call at Limit for ' + i+ '\'s OHLCV data...switching to another API key, and sleep for 5 seconds..')
                            if api == 0:
                                api = 1
                            elif api == 1:
                                api = 0
                            time.sleep(5)
                    new = new.drop(new.index.intersection(csv_data.index)) #resetting new data by dropping existing ones if there are any
                    csv_data = csv_data.append(new)
                    csv_data.to_csv(os.path.join(self.csv_path,
                            '{file_name}.{file_extension}'.format(file_name = i,
                            file_extension = 'csv')))
                else:
                    print(i+ '\'s ' + 'OHLCV data is up to date. No update needed.')
                    # other, aka latest csv's latest timestamp is up to date, we won't do anything
                    pass
            elif check == False: # if no data file exists
                print(i+ '\'s ' + 'OHLCV data not found in database. Downloading and saving latest data...')
                new = None
                while type(new) != pd.DataFrame:
                    try:
                        ts = TimeSeries(key=api_keys[api], output_format = 'pandas')
                        new = ts.get_intraday(symbol = i, interval = interval, outputsize = 'full')[0]
                    except ValueError:
                        print('API Call at Limit for ' + i+ '\'s OHLCV data...switching to another API key, and sleep for 5 seconds..')
                        if api == 0:
                            api = 1
                        elif api == 1:
                            api = 0
                        time.sleep(5)
                new.to_csv(os.path.join(self.csv_path,
                            '{file_name}.{file_extension}'.format(file_name = i,
                            file_extension = 'csv')))
    
    def add_data(self,symbols,periods=None,sma=False,ewma=False,
                arith_ret=False,hpfilter=False,log_ret=False,d1close=False,d2close=False):
        #use to add any additional calculations for backtesting data
        #all calculations are performed on close price
        #default assigned to minimize errors
        print('--------------------------------------------------------')
        print('----------ADDING REQUESTED DATA FROM STRATEGY-----------')
        print('--------------------------------------------------------')
        if sma == True:
            print('-> Simple Moving Average (SMA) with periods',str(periods))
        if ewma == True:
            print('-> Exponentially Weighted Moving Average (EWMA) with periods',str(periods))
        if arith_ret == True:
            print('-> Arithmetic Daily Returns')
        if hpfilter == True:
            print('-> HP (Hodrick-Prescott) Filter')
        if log_ret == True:
            print('-> Logarithmic Daily Returns (log of Arithmetic)')
        else:
            print('--> NONE')
        print('--------------------------------------------------------')
        if type(periods) == list:
            index_to_drop = max(periods)-1 #dropping indexes that contain NaN, which resulted from periodic calculations
        elif (arith_ret == True) or (log_ret == True):
            index_to_drop = 1
        else:
            index_to_drop = 0
        self.timestamp = self.timestamp.drop(self.timestamp[:index_to_drop])
        for i in symbols:
            if sma == True:
                for p in periods:
                    self.symbol_data[i]['sma'+str(p)] = self.symbol_data[i]['close'].rolling(p).mean()
            if ewma == True:
                for p in periods:
                    self.symbol_data[i]['ewma'+str(p)] = self.symbol_data[i]['close'].ewm(span=p).mean()
            if arith_ret == True:
                self.symbol_data[i]['arith_ret'] = (self.symbol_data[i]['close']/self.symbol_data[i]['close'].shift(1)) - 1
            if hpfilter == True:
                hpfilter = sm.tsa.filters.hpfilter(self.symbol_data[i]['close'])
                self.symbol_data[i]['hptrend'] = hpfilter[1]
                self.symbol_data[i]['hpnoise'] = hpfilter[0]
            if log_ret == True:
                self.symbol_data[i]['log_ret'] = np.log(self.symbol_data[i]['close']/self.symbol_data[i]['close'].shift(1))
            if d1close == True:
                self.symbol_data[i]['d1close'] = self.symbol_data[i]['close'] - self.symbol_data[i]['close'].shift(1)
            if d2close == True:
                self.symbol_data[i]['d2close'] = self.symbol_data[i]['close'] - self.symbol_data[i]['close'].shift(1)
            self.symbol_data[i] = self.symbol_data[i].drop(self.symbol_data[i].index[:index_to_drop])



                
                
