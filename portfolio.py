import pandas as pd
import numpy as np
import datetime

from math import floor
from abc import ABCMeta, abstractmethod

from event import FillEvent, OrderEvent

class Portfolio(object):

    __metaclass__  = ABCMeta

    @abstractmethod
    def update_holdings(self,event):
        raise NotImplementedError('Implement update_holdings() to continue')

    @abstractmethod
    def update_signal(self,event):
        raise NotImplementedError('Implement update_signal() to continue')
    
    @abstractmethod
    def update_portfolio(self,event):
        raise NotImplementedError('Implement update_portfolio() to continue')


# ------------------------------------------------------------------------------------------------------
# SAMPLE BASIC PORTFOLIO (written by Jack)
# written for backtesting purposes
# ------------------------------------------------------------------------------------------------------
class SamplePortfolio(Portfolio):

    def __init__(self, bars, events, initial_balance = 100000.0):
        self.bars = bars
        self.events = events
        self.symbols = self.bars.symbols
        self.initial_balance = initial_balance
        self.cash_balance = initial_balance
        self.daily_logged_stamps = {} # for logging to drop when performing analysis for logging
        self.portfolio_value = pd.DataFrame(columns =self.symbols+['Cash Balance','Total Value']) # indexed over time
        self.holdings = {} # holdings tracks all holdings, indexed over time
        initial_value = pd.Series(data = float(0),index=list(self.portfolio_value.columns),name=self.bars.latest_stamps[-1])
        initial_value['Cash Balance'] = self.cash_balance
        initial_value['Total Value'] = self.cash_balance
        self.portfolio_value = self.portfolio_value.append(initial_value)
        for s in self.symbols:
            self.holdings[s] = pd.DataFrame(columns = ['close','position','value'])
            self.holdings[s] = self.holdings[s].append(pd.Series(data=float(0),index=['close','position','value'],name=self.bars.latest_stamps[-1]))
            self.holdings[s].at[self.holdings[s].index[-1],'close'] = self.bars.get_latest_bars(s).close

    def update_portfolio(self,event):
        # updating portfolio after order was executed
        # position---> (-) = SELL, (+) = BUY, 0 = No position
        if event.order_type == 'MARKET':
            if event.action == 'BUY':
                close = self.bars.get_latest_bars(event.symbol,N=1).close
                new_position = self.holdings[event.symbol].at[event.stamp,'position'] + event.shares
                new_value = new_position*close
                new_cash = self.cash_balance - (event.shares*close + event.commission)
                self.holdings[event.symbol].at[event.stamp,'position'] = new_position
                self.holdings[event.symbol].at[event.stamp,'value'] = new_value
                self.cash_balance = new_cash
            elif event.action == 'SELL':
                close = self.holdings[event.symbol].at[event.stamp,'close']
                new_position = self.holdings[event.symbol].at[event.stamp,'position'] - event.shares
                new_value = new_position*close
                new_cash = self.cash_balance + (event.shares*close + event.commission)
                self.holdings[event.symbol].at[event.stamp,'position'] = new_position
                self.holdings[event.symbol].at[event.stamp,'value'] = new_value
                self.cash_balance = new_cash
            else:
                pass # NO BUY OR SELL WAS MADE AND WE ALREADY UPDATED HOLDINGS VALUES, THROUGH UPDATE_HOLDINGS(), AS SOON AS THE NEW BAR WAS LAUNCH,
            self.update_portfolio_value(event)

    def update_portfolio_value(self,event):
        # called for MarketEvent and FillEvent
        if event.stamp in self.portfolio_value.index:
            new_value = self.holdings[event.symbol].at[event.stamp,'value']
            self.portfolio_value.at[event.stamp,event.symbol] = new_value
            self.portfolio_value.at[event.stamp,'Cash Balance'] = self.cash_balance
            total_value = self.portfolio_value.loc[event.stamp].drop('Total Value').sum()
            self.portfolio_value.at[event.stamp,'Total Value'] = total_value
        else:
            # if event stamp isn't in portfolio_value, meaning it's new so we'll craft a new data row to append
            values = []
            for s in self.symbols:
                values.append(self.holdings[s].at[event.stamp,'value'])
            data = pd.Series(data = values,index = self.symbols,name=event.stamp) # set new index as event stamp
            data['Cash Balance'] = self.cash_balance
            data['Total Value'] = data.sum()
            self.portfolio_value = self.portfolio_value.append(data)


    def generate_order(self,event):
        # Strategy has access to all components except execution
        order = OrderEvent(event.symbol,shares = event.shares, action = event.action,
                            order_type = event.order_type,limit_price = event.limit_price,
                            stop_price = event.stop_price, stamp = event.stamp)
        print(order)
        return order

    def update_signal(self,event):
        if event.type == 'SIGNAL':
            order = self.generate_order(event)
            self.events.put(order)

    def update_holdings(self,event):
        # Method accounts for more than one bar missing
        # PURPOSE: add missing stamps between our current holdings and dataframe
        if event.type == 'MARKET':
            new_stamp = event.stamp
            for s in self.symbols:
                new_bar = self.bars.latest_symbol_data[s].loc[new_stamp]
                if self.holdings[s].empty:
                    to_update = pd.Series(data=float(0), index=['close','position'])
                else:
                    to_update = self.holdings[s].loc[self.holdings[s].index[-1]].drop('value') #set as the last holding and modify next
                to_update.name = new_bar.name
                to_update.close = new_bar.close
                to_update['value'] = to_update.prod()
                self.holdings[s] = self.holdings[s].append(to_update)
            self.update_portfolio_value(event)
            if (self.bars.interval[-1].lower() != 'd'):
                self.daily_portfolio_logging()

    def daily_portfolio_logging(self):
        # serve as a function to analyze latest stamps to determine whether to spit out a printed report or not
        # saves logs to daily_logged_stamps
        stamps = self.bars.latest_stamps
        dstamps = pd.to_datetime(stamps)
        if len(dstamps) == 1: # first bar
            pass
        elif dstamps[-1].date() == dstamps[-2].date():
            # if we're still in the same day, we won't do anything
            pass
        elif dstamps[-1].date() != dstamps[-2].date():
            # if we're in the next day, we'll print our report
            if len(self.daily_logged_stamps) == 0:
                stamps_to_log = stamps[:-1] # exclude latest stamp since it's in the next day
            else:
                to_drop = None
                for i in self.daily_logged_stamps:
                    if type(to_drop) != pd.Index:
                        to_drop = self.daily_logged_stamps[i]
                    else:
                        to_drop = to_drop.append(self.daily_logged_stamps[i])
                stamps_to_log = stamps[:-1].drop(to_drop)
            self.daily_logged_stamps[dstamps[-2].date()] = stamps_to_log # update logged_stamps for future updates
            pfolio_value = self.portfolio_value.loc[stamps_to_log]
            total_value = pfolio_value['Total Value'].describe()
            stamp_header = dstamps[-2].strftime("%B %d, %Y")
            print('<<-------| PORTFOLIO VALUE REPORT:',stamp_header,'|------->>')
            print(total_value)


        
        