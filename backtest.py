#-----IMPORT OTHER NECESSARY MODULES-----#
import datetime
import queue
from queue import Queue
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm 
#-----IMPORT BACKTESTING COMPONENTS-----#
import event
from broker import BasicBroker
from data import AlpacaDataFrame
from portfolio import SamplePortfolio
from strategy import PortfolioSharpeMaximization

#---SET ASSETS TO BE TRADED AND LOCATION TO IMPORT ASSETS DATA---#

symbols = ['SPY','MSFT','AAPL','AMZN','BRK.B','JNJ',
           'JPM','GOOG','FB','GOOGL','XOM','BAC',
           'UNH','V','PFE','PG','INTC','CVX','VZ','BA','T']
csv_path = os.path.join(os.getcwd(),'database')

#---INITIALIZING COMPONENTS TO READY FOR BACKTEST---#

Events = Queue()

DataFrame = AlpacaDataFrame(events = Events, csv_path = csv_path,
                         symbols = symbols,interval='1D')

Portfolio = SamplePortfolio(bars = DataFrame, events = Events)
Strategy = PortfolioSharpeMaximization(bars = DataFrame, events = Events,
                            portfolio = Portfolio)
Broker = BasicBroker(events = Events)


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
                Portfolio.update_holdings(event) 
                Strategy.calculate_signals(event)
            elif event.type == 'SIGNAL':
                Portfolio.update_signal(event)
            elif event.type == 'ORDER':
                Broker.execute_order(event)
            elif event.type == 'FILL':
                Portfolio.update_portfolio(event)

