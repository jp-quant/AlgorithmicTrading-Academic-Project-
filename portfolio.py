import pandas as pd
import numpy as np
import datetime

from math import floor
from abc import ABCMeta, abstractmethod

from event import FillEvent, OrderEvent

class Portfolio(object):

    __metaclass__  = ABCMeta

    @abstractmethod
    def update_market(self,event):
        raise NotImplementedError('Implement update_market() to continue')

    @abstractmethod
    def update_signal(self,event):
        raise NotImplementedError('Implement update_signal() to continue')
    
    @abstractmethod
    def update_portfolio(self,event):
        raise NotImplementedError('Implement update_fill() to continue')


# ------------------------------------------------------------------------------------------------------
# SAMPLE PORTFOLIO (written by Jack)
# accounting future integration to live trading
# ------------------------------------------------------------------------------------------------------
class SamplePortfolio(Portfolio):

    def __init__(self, bars, events, initial_balance = 1000.0):
        self.bars = bars
        self.events = events
        self.symbols = self.bars.symbols
        self.initial_balance = initial_balance
        self.cash_balance = initial_balance
        # all_holdings tracks all holdings, indexed over time
        self.all_holdings = {}
        self.current_holdings = {}
        self.daily_logged_stamps = [] # for logging to drop when performing analysis for logging
        self.portfolio_value = pd.DataFrame(columns =self.symbols+['Cash Balance','Total Value']) # indexed over time
        for s in self.symbols:
            self.all_holdings[s] = pd.DataFrame(columns = ['close','position','value'])
            self.current_holdings[s] = pd.Series(data = 0.0, index =['close','position','value'])

    def update_portfolio(self,event):
        # updating portfolio after order was executed
        # position---> (-) = SELL, (+) = BUY, 0 = No position
        if event.order_type == 'BUY':
            self.current_holdings[event.symbol]['position'] += event.quantity
            self.current_holdings[event.symbol]['value'] = self.current_holdings[event.symbol]['close']*self.current_holdings[event.symbol]['position']
            self.cash_balance -= event.quantity*self.current_holdings[event.symbol]['close']
        elif event.order_type == 'SELL':
            self.current_holdings[event.symbol]['position'] -= event.quantity
            self.current_holdings[event.symbol]['value'] = self.current_holdings[event.symbol]['close']*self.current_holdings[event.symbol]['position']
            self.cash_balance += event.quantity*self.current_holdings[event.symbol]['close']
        else:
            pass # NO BUY OR SELL WAS MADE AND WE ALREADY UPDATED PORTFOLIO VALUE, THROUGH UPDATE_MARET(), AS SOON AS THE NEW BAR WAS LAUNCH,
        if (self.all_holdings[event.symbol].empty) or (event.stamp not in self.all_holdings[event.symbol].index):
            self.all_holdings[event.symbol] = self.all_holdings[event.symbol].append(self.current_holdings[event.symbol])
        if (self.portfolio_value.empty) or (event.stamp not in self.portfolio_value.index):
            # if timestamp isn't in portfolio_value, meaning it's new so we'll craft a new data row to append
            values = []
            for s in self.symbols:
                values.append(self.current_holdings[s]['value'])
            data = pd.Series(data = values,index = self.symbols,name=self.bars.latest_stamps[-1]) # set new index as latest stamp
            data['Cash Balance'] = self.cash_balance
            data['Total Value'] = data.sum()
            self.portfolio_value = self.portfolio_value.append(data)
        elif event.stamp in self.portfolio_value.index:
            self.portfolio_value.at[event.stamp,event.symbol] = self.current_holdings[event.symbol]['value']
            self.portfolio_value.at[event.stamp,'Cash Balance'] = self.cash_balance
            total_value = self.portfolio_value.loc[event.stamp].drop('Total Value').sum()
            self.portfolio_value.at[event.stamp,'Total Value'] = total_value


    def generate_order(self,event):
        # strategy has access to all components except execution
        order = OrderEvent(event.symbol,event.stamp,event.action,event.quantity)
        return order

    def update_signal(self,event):
        if event.type == 'SIGNAL':
            order = self.generate_order(event)
            self.events.put(order)

    def update_market(self,event):
        # Method accounts for more than one bar missing
        # PURPOSE: add missing stamps between our current holdings and dataframe
        for s in self.symbols:
            bar = self.bars.get_latest_bars(s,N=1)[-1]
            self.current_holdings[s].name = bar.name
            self.current_holdings[s]['close'] = bar['close']
            self.current_holdings[s]['value'] = self.current_holdings[s]['position']*bar['close']
        self.daily_portfolio_logging()

    def daily_portfolio_logging(self):
        # serve as a function to analyze latest stamps to determine whether to spit out a printed report or not
        # saves logs to  self.daily_logged_stamps
        latest_stamps = self.bars.latest_stamps
        if len(latest_stamps) == 1: # first bar
            pass
        elif datetime.datetime.strptime(latest_stamps[-1],'%Y-%m-%d %H:%M:%S').date() == datetime.datetime.strptime(latest_stamps[-2],'%Y-%m-%d %H:%M:%S').date():
            # if we're still in the same day, we won't do anything
            pass
        elif datetime.datetime.strptime(latest_stamps[-1],'%Y-%m-%d %H:%M:%S').date() != datetime.datetime.strptime(latest_stamps[-2],'%Y-%m-%d %H:%M:%S').date():
            # if we're in the next day, we'll print our report
            if len(self.daily_logged_stamps) == 0:
                stamps_to_log = latest_stamps[:-1] # exclude latest stamp since it's in the next day
                self.daily_logged_stamps.append(stamps_to_log) #assign /create logged stamps record
            else:
                to_log = []
                for i in self.daily_logged_stamps:
                    to_log += i
                stamps_to_log = pd.Index(latest_stamps[:-1]).drop(pd.Index(to_log))
                self.daily_logged_stamps.append(list(stamps_to_log)) # update logged_stamps for future updates
            portfolio_value = self.portfolio_value.loc[stamps_to_log]
            total_value = portfolio_value['Total Value'].describe()
            stamp_header = datetime.datetime.strptime(latest_stamps[-2],'%Y-%m-%d %H:%M:%S').strftime("%B %d, %Y")
            print('<<-------| PORTFOLIO VALUE REPORT:',stamp_header,'|------->>')
            print(total_value)


        
        