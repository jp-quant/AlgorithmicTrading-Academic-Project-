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
import pandas as pd
import errno
import oandapy as opy


class StartProgram:

           
    def __init__(self,
                 api,
                 market,
                 opy_start,
                 opy_end,
                 symbols = ['AAPL','CALD','ENVA'],
                 interval = ['15min','30mins']):
        
        #setting variables to self
        self.api= api
        self.ticks = 0
        self.symbols = symbols
        self.interval = interval
        self.market = market
        self.opy_start = opy_start
        self.opy_end = opy_end
        
        #Use wrapper to import data and save them automatically
        ts = TimeSeries(key=api, output_format = 'pandas')
        oanda = opy.API(environment='practice', access_token= api)
        
        #If market is stocks, we use Alpha Vantage API
        if market == 'stocks':
                for i in symbols:
                    for x in interval:
                        if x.lower() == 'daily':
                            data, metadata = ts.get_daily(symbol = i, outputsize= 'full')
                        elif x.lower() == 'daily adjusted':
                            data, metadata = ts.get_daily_adjusted(symbol = i, outputsize= 'full')
                        elif x.lower() == 'weekly':
                            data, metadata = ts.get_weekly(symbol = i, outputsize= 'full')
                        elif x.lower() == 'weekly adjusted':
                            data, metadata = ts.get_weekly_adjusted(symbol = i, outputsize= 'full')
                        elif x.lower() == 'monthly':
                            data, metadata = ts.get_monthly(symbol = i, outputsize= 'full')
                        elif x.lower() == 'monthly adjusted':
                            data, metadata = ts.get_monthly_adjusted(symbol = i, outputsize= 'full')
                        elif x.lower() == '1min' or '5min' or '15min' or '30min' or '60min':
                            data, metadata = ts.get_intraday(symbol = i, interval = x, outputsize= 'full')
                        else:
                            exit
                        location = os.path.join(os.getcwd(),'database',market,i,x)
                        print 'Downloading data for ' + i + ' at ' + x + ' interval' + '...'
                        try:
                            os.makedirs(location)
                        except OSError as e:
                            if e.errno != errno.EEXIST:
                                raise
                        data.to_csv(location + '/'+ datetime.datetime.now().strftime('%Y-%m-%d') +'.csv')
                
        #If market is forex, we use Oanda API, since Alpha Vantage only provide instant real time, not historical data on forex (for backtesting purposes)
        if market == 'forex':
            for i in symbols:
                for x in interval:
                    data = oanda.get_history(instrument= i,  # our instrument
                         start= opy_start,  # start data
                         end= opy_end,  # end date
                         granularity='M5')
                    location = os.path.join(os.getcwd(),'database',market,i,opy_start + ' to ' + opy_end,x)
                    df = pd.DataFrame(data['candles']).set_index('time')
                    df.index = pd.DatetimeIndex(df.index)
                    print 'Downloading data for ' + i + ' at ' + x + ' interval' + ' at specificed time frame...'
                    try:
                            os.makedirs(location)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise
                    df.to_csv(location + '/'+ opy_start + ' to ' + opy_end +'.csv')
                    
