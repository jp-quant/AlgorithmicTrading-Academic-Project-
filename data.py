import alpaca_trade_api as tradeapi
import matplotlib.pyplot as plt
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
import talib

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
    #use to add sma data to the dataframe
    def add_data(self,symbols,periods,sma,ema,cumreturns,hpfilter):
        raise NotImplementedError('implement add_sma to proceed') 

    # add more abstract methods if needed 


   
class AlpacaDataFrame(DataFrame):

    def __init__(self, events, csv_path, symbols,interval):
        #-----Initialize params-----#
        self.events = events
        self.csv_path = csv_path +'/'+interval.lower()
        self.symbols = symbols
        self.interval = interval
        #---------------------------#
        self.symbol_data = {}
        self.bars_generator = {}
        self.timestamps = None #timestamp will be set after load.csv() is run
        self.latest_stamps = None #use to track our current time index
        self.latest_symbol_data = {}
        self.continue_backtest = True
        '''
        self.alpaca_api_keys = {'key_id':[YOUR KEY ID],
                                'secret_key':[YOUR SECRET KEY ID]}
        self.alpaca_api = tradeapi.REST(self.alpaca_api_keys['key_id'],self.alpaca_api_keys['secret_key'])
        # After initializing all variables, we load all symbols' csv files (OHLCV) into symbol_data as generators
        self.market_calendar = self.alpaca_api.get_calendar()
        '''
        self.initialize_df(interval=self.interval)
        self.load_warm_up(0.25)

    #***
    def initialize_df(self,interval):
        #IMPORTANT: THE ORIGINAL DATA VETTED IN update_database
        #           NEED TO BE FIXED TO ['open','high','low','close','volume']
        indexes = None
        columns = ['open','high','low','close','volume']
        not_seen = []
        for i in self.symbols:
            path_check = os.path.exists(self.csv_path+'/'+i+'.csv') # checking for filled data
            if path_check == True:
                pass
            elif path_check == False:
                not_seen.append(i)

        if len(not_seen) == 0:
            print('Data available for the requested symbol(s)')
            answers = ['y','n']
            db_check = input('Perform update (requires internet) for potential new data? (Y/N): ')
            while str(db_check).lower() not in answers:
                db_check = input('Invalid Input. Please enter \'Y\' for YES and \'Y\' for NO (Y/N): ')

            if str(db_check).lower() == 'y':
                self.update_database(symbols=self.symbols,interval=self.interval)
            elif str(db_check).lower() == 'n':
                pass
        else:
            print('Database is missing data for the following symbol(s): ')
            print('------------------------')
            for i in not_seen:
                print(i)
            print('------------------------')
            print('Commencing Automatic Database Update...')
            self.update_database(symbols = self.symbols,interval=self.interval)
        print('Initializing DataFrame...')
        for i in self.symbols:
            self.symbol_data[i] = pd.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i,
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            
            self.symbol_data[i].columns = columns # clean up columns
            self.symbol_data[i] = self.symbol_data[i].sort_index() #sort index to make sure it's monotonic
            # IF WE'RE DATAFRAME INTERVAL IS DAILY, WE'LL JUST GET RID OF TIME FOR THE INDEXES
            if interval[-1] == 'D':
                self.symbol_data[i].index = [d.split(' ')[0] for d in self.symbol_data[i].index]
            if indexes is None:
                indexes = self.symbol_data[i].index
            else:
                indexes.union(self.symbol_data[i].index)
        self.timestamps = indexes
        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index=indexes)
            self.bars_generator[i] = self.symbol_data[i].iterrows()
    
    #***
    def update_database(self,symbols, interval):
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
                    print(i+ '\'s ' + 'OHLCV data is outdated. Updating...')
                    result = self.get_alpaca_historic(i,interval)
                    result = self.clean_symbol_data(result)
                    result = result.drop(result.index.intersection(csv_data.index)) #resetting result data by dropping existing ones if there are any
                    csv_data = csv_data.append(result)
                    csv_data.to_csv(os.path.join(self.csv_path,
                                '{file_name}.{file_extension}'.format(file_name = i,
                                file_extension = 'csv')))

                else:
                    print(i+ '\'s ' + 'OHLCV data is up to date. No update needed.')
                    pass
            elif check == False: # if no data file exists
                print(i+ '\'s ' + 'OHLCV data not found in database. Downloading and saving latest data...')
                if os.path.exists(self.csv_path):
                    pass
                else:
                    os.makedirs(self.csv_path)
                result = self.get_alpaca_historic(i,interval)
                result = self.clean_symbol_data(result)
                result.to_csv(os.path.join(self.csv_path,
                            '{file_name}.{file_extension}'.format(file_name = i,
                             file_extension = 'csv'))) 
    
    #*
    def get_market_hours(self,y=None,m=None,d=None,mode = 'custom'):
        if mode == 'today':
            today = datetime.date.today()
            for i in self.market_calendar:
                year,month,day = i._raw['date'].split('-')
                if today.year != int(year):
                    pass
                elif today.month != int(month):
                    pass
                elif today.day != int(day):
                    pass
                else:
                    open_time = i._raw['open']
                    close_time = i._raw['close']
                    break
            return {'open':open_time,
                    'close':close_time}
        elif (mode == 'custom') and (type(y) == int) and (type(m) == int) and(type(d) == int):
            for i in self.market_calendar:
                year,month,day = i._raw['date'].split('-')
                if y != int(year):
                    pass
                elif m != int(month):
                    pass
                elif d != int(day):
                    pass
                else:
                    open_time = i._raw['open']
                    close_time = i._raw['close']
                    break
            return {'open':open_time,
                    'close':close_time}
        else:
            print('TF enter the proper parameters pls')
    
    #**
    def get_alpaca_historic(self,symbol,interval,years_ago=10):
        # we will determine the limit of bars needed by years ago entered
        start_year = datetime.datetime.today().year - years_ago
        start_date = str(start_year)+"-01-01T00:00:00.000Z" # Start date for the market data in ISO8601 format
        new_data = self.alpaca_api.get_barset(symbol,interval,start=start_date)[symbol]
        stamps = []
        opens  = []
        closes = []
        highs = []
        lows = []
        volumes = []
        for bar in new_data:
            stamps.append(str(datetime.datetime.strftime(bar.t,'%Y-%m-%d %H:%M:%S')))
            opens.append(bar.o)
            closes.append(bar.c)
            highs.append(bar.h)
            lows.append(bar.l)
            volumes.append(bar.v)
        stamps = np.array(stamps)
        opens = np.array(opens,dtype=np.float64)
        closes = np.array(closes,dtype=np.float64)
        highs = np.array(highs,dtype=np.float64)
        lows = np.array(lows,dtype=np.float64)
        volumes = np.array(volumes,dtype=np.float64)

        result = pd.DataFrame()
        result['open'] = pd.Series(data = opens,index=stamps)
        result['high'] = pd.Series(data=highs,index=stamps)
        result['low'] = pd.Series(data=lows,index=stamps)
        result['close'] = pd.Series(data=closes,index=stamps)
        result['volume'] = pd.Series(data=volumes,index=stamps)

        

        return result

    def clean_symbol_data(self,symbol_data):
        if ((self.interval.lower() == 'day') or (self.interval[-1].lower() == 'd')):
            return symbol_data
        else:
            df = pd.DataFrame().append(symbol_data)
            df = self.fill_intraday(df)
            return df
    #***
    def fill_intraday(self,symbol_data,interval=None):
        # fill interval for symbol_data (for raw data downloaded)
        #---First we will split our df into day by day---#
        all_dfs = []
        df = pd.DataFrame().append(symbol_data)
        for group in df.groupby(pd.to_datetime(df.index).date):
	        all_dfs.append(group[1])

        all_dfs = all_dfs[1:]
        
        #---we will make a df_m with the consistent time interval to reindex---#
        #--- open = 9am, close = 5pm ---#
        df_m = pd.DataFrame(index=pd.Index(['2019-01-18 9:30:00', '2019-01-18 15:59:00'])) #string here is arbitrary as long as format fulfills frequency propagation and datetime conversion
        df_m.index = pd.to_datetime(df_m.index)
        if interval is None:
            df_m = df_m.asfreq(self.interval)
        else:
            df_m = df_m.asfreq(interval)
        df_m.index = pd.Index([str(dt) for dt in df_m.index])

        #---Now we will use df_m's time index to "frequencize" our whole df day by day
        new_dfs = []
        for df in all_dfs:
            date_str = df.index[0].split(' ')[0]
            new_indexes = pd.Index([(date_str+' '+dt.split(' ')[1]) for dt in df_m.index])
            new_df = df.reindex(new_indexes)  
            new_dfs.append(new_df)

        return pd.concat(new_dfs)
    
    def utc_to_est(self,symbol_data):
        # convert stamps in symbol_data from UTC -> EST
        df = pd.DataFrame().append(symbol_data)
        df.index = pd.to_datetime(df.index)
        df = df.tz_localize('UTC').tz_convert('EST')
        df.index = pd.Index([str(dt).split('-05:00')[0] for dt in df.index])
        return df

    def add_data(self,symbols,periods=None,sma=False,ema=False,
                arith_ret=False,hpfilter=False,log_ret=False,d1close=False,d2close=False,
                rsi=False,ewma=False,wma=False,natr=False):
        #use to add any additional calculations for backtesting data
        #all calculations are performed on close price
        print('--------------------------------------------------------')
        print('----------ADDING REQUESTED DATA FROM STRATEGY-----------')
        print('--------------------------------------------------------')
        if sma == True:
            print('-> Simple Moving Average (SMA) with periods',str(periods))
        if ema == True:
            print('-> Exponentially Moving Average (EMA) with periods',str(periods))
        if wma == True:
            print('-> Weighted Moving Average (WMA) with periods',str(periods))
        if ewma == True:
            print('> Exponentially Weighted Moving Average (EWMA) with periods',str(periods))
        if rsi == True:
            print('-> Relative Strength Index (RSI) with periods', str(periods))
        if natr == True:
            print('-> Normalized Average True Range (NATR) with periods', str(periods))
        if arith_ret == True:
            print('-> Arithmetic Daily Returns')
        if hpfilter == True:
            print('-> HP (Hodrick-Prescott) Filter')
        if log_ret == True:
            print('-> Logarithmic Daily Returns (log of Arithmetic)')
        if d1close == True:
            print('-> First-Order Difference')
        if d2close == True:
            print('-> Second-Order Difference')
        print('--------------------------------------------------------')
        new_stamps = None
        df = {}
        for i in self.symbol_data:
            df[i] = pd.DataFrame().append(self.symbol_data[i]).ffill()
        for i in symbols:
            if sma == True:
                for p in periods:
                    self.symbol_data[i]['sma'+str(p)] = talib.SMA(df[i]['close'],p)
            if wma == True:
                for p in periods:
                    self.symbol_data[i]['wma'+str(p)] = talib.WMA(df[i]['close'],p)
            if ema == True:
                for p in periods:
                    self.symbol_data[i]['ema'+str(p)] = talib.EMA(df[i]['close'],p)
            if ewma == True:
                for p in periods:
                    self.symbol_data[i]['ewma'+str(p)] = talib.EMA(talib.WMA(df[i]['close'],p),p)
            if arith_ret == True:
                self.symbol_data[i]['arith_ret'] = (df[i]['close']/df[i]['close'].shift(1)) - 1
            if hpfilter == True:
                hpfilter = sm.tsa.filters.hpfilter(df[i]['close'])
                self.symbol_data[i]['hptrend'] = hpfilter[1]
                self.symbol_data[i]['hpnoise'] = hpfilter[0]
            if log_ret == True:
                self.symbol_data[i]['log_ret'] = np.log(df[i]['close']/df[i]['close'].shift(1))
            if d1close == True:
                self.symbol_data[i]['d1close'] = df[i]['close'] - df[i]['close'].shift(1)
            if d2close == True:
                self.symbol_data[i]['d2close'] = df[i]['close'] - df[i]['close'].shift(1)
            if rsi == True:
                for p in periods:
                    self.symbol_data[i]['rsi'+str(p)] = talib.RSI(df[i]['close'],p)
            if natr == True:
                for p in periods:
                    self.symbol_data[i]['natr'+str(p)] = talib.NATR(df[i]['high'],df[i]['low'],df[i]['close'],p)
            
            self.symbol_data[i] = self.symbol_data[i].drop(self.symbol_data[i].head(max(periods)+10).drop(self.symbol_data[i].head(max(periods)+10).dropna().index).index)
            if new_stamps is None:
                new_stamps = self.symbol_data[i].index
            else:
                new_stamps.union(self.symbol_data[i].index)
        self.timestamps = new_stamps
        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index=new_stamps)
            self.bars_generator[i] = self.symbol_data[i].iterrows()

    def load_warm_up(self,percent):
        count = int(percent*len(self.timestamps))
        print('---|LOADING',str(count),'WARM-UP BARS AS',str(percent*100)+'%',' OF AVAILABLE HISTORICAL DATA|---')
        self.latest_stamps = self.timestamps[:count]
        for s in self.symbols:
            self.latest_symbol_data[s] = self.symbol_data[s].loc[self.latest_stamps]
            self.bars_generator[s] = self.symbol_data[s].drop(self.latest_symbol_data[s].index).iterrows()

    def get_new_bar(self,symbol):
        new_bar = next(self.bars_generator[symbol])
        return new_bar[1] #return a pandas series to be appended to latest_symbol_data

    def update_bars(self):
        #before updating bars, we need to grab the next timestamp and delete it from our existing ones
        try:
            for s in self.symbols:
                bar = self.get_new_bar(s)
                if bar.name not in list(self.latest_stamps):
                    self.latest_stamps = self.latest_stamps.append(pd.Index([bar.name]))
                self.latest_symbol_data[s] = self.latest_symbol_data[s].append(bar)
            self.events.put(MarketEvent(self.latest_stamps[-1])) #FIRST START, IMPORTANT
        except StopIteration:
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
            elif N == 1:
                return bars_list.iloc[-N]
            elif N < 0:
                print('N needs to be an integer >= 0')
            elif N > 0:
                return bars_list.iloc[-N:]