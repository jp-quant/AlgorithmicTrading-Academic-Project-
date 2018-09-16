#-----IMPORT BACKTESTING COMPONENTS-----#
import event
import broker
import data
import portfolio
import strategy
#-----IMPORT OTHER NECESSARY MODULES-----#
import queue
import os
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm # HPFilter
from statsmodels.tsa.seasonal import seasonal_decompose #ETS
from statsmodels.tsa.stattools import adfuller #unit root test for stationarity
from scipy.optimize import minimize # portfolio optimizations

#---SET ASSETS TO BE TRADED AND LOCATION TO IMPORT ASSETS DATA---#
symbols = ['AAPL','GOOG','AMZN','NVDA','TSLA','NFLX','FB','AMD','CSCO','INTC']
csv_path = os.path.join(os.getcwd(),'database')

#---INITIALIZING COMPONENTS TO READY FOR BACKTEST---#
Events = queue.Queue()
Broker = broker.BasicBroker(events = Events)
DataFrame = data.CSVData(events = Events, csv_path = csv_path, symbols = symbols)
Portfolio = portfolio.SamplePortfolio(bars = DataFrame, events = Events)
Strategy = strategy.SampleStrategy(bars = DataFrame, events = Events, portfolio = Portfolio)
    
#--------START TRADING--------#
print('BACKTESTING IN PROGRESS...')
while True:
    if DataFrame.continue_backtest == True:
        DataFrame.update_bars()
    else:
        break
  
    while True:
        try:
            event = Events.get(False)
        except queue.Empty:
            break
        
        if event is not None:
            if event.type == 'MARKET':
                Portfolio.update_market(event) 
                Strategy.calculate_signals(event)
            elif event.type == 'SIGNAL':
                Portfolio.update_signal(event)
            elif event.type == 'ORDER':
                Broker.execute_order(event)
            elif event.type == 'FILL':
                Portfolio.update_portfolio(event)


