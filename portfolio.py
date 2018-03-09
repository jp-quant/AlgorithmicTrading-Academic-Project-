import pandas as pd
import numpy as np
import datetime

from math import floor
from abc import ABCMeta, abstractmethod

from event import FillEvent, OrderEvent
from performance import create_sharpe_ratio, create_drawdowns

class Portfolio(object):

    __metaclass__  = ABCMeta

    @abstractmethod
    def update_signal(self,event):
        raise NotImplementedError('Implement update_signal() to continue')
    
    @abstractmethod
    def update_fill(self,event):
        raise NotImplementedError('Implement update_fill() to continue')
    
    # This is the NaivePortfolio class. 
    # It is designed to handle position sizing and current holdings,
    # but will carry out trading orders in a "dumb" manner by simply
    # sending them directly to the brokerage with a predetermined fixed quantity size, irrespective of cash held. 

class NaivePortfolio(Portfolio):

    def __init__(self, bars, events, start_date, initial_balance = 100000.0):

        self.bars = bars
        self.events = events
        self.symbols = self.bars.symbols
        self.start_date = start_date
        self.initial_balance = initial_balance
        self.all_positions = self.construct_all_positions()
        self.current_positions = {symbol: 0.0 for symbol in self.symbols}
        self.all_holdings = self.construct_all_holdings()
        self.current_holdings = self.construct_current_holdings()
        
    def update_fill(self,event):
        if event.type == 'FILL':
            self.update_positions(event)
            self.update_holdings(event)

    def construct_all_positions(self):
        d = {symbol: 0.0 for symbol in self.symbols}
        d['datetime'] = self.start_date
        return d
        
    def construct_all_holdings(self):
        d = {symbol: 0.0 for symbol in self.symbols}
        d['cash'] = self.initial_balance
        d['comission'] = 0.0
        d['total'] = self.initial_balance
        return d

    def construct_current_holdings(self):
        d = d = {symbol: 0.0 for symbol in self.symbols}
        d['cash'] = self.initial_balance
        d['commission'] = 0.0
        d['total'] = self.initial_balance
        return d
        
    def update_timeindex(self,event):
        bars = {symbol: self.bars.get_latest_bars(symbol,N=1) for symbol in self.symbols}
        positions = {symbol: self.current_positions[symbol] for symbol in self.symbols}
        self.all_positions.update(positions)

        dh = {symbol: 0 for symbol in self.symbols}
        dh['datetime'] = bars[self.symbols[0]][0][1]
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']

        for i in self.symbols:
            market_value = self.current_positions[i] * bars[i][0][5]
            dh[i] = market_value
            dh['total'] += market_value

        self.all_holdings.update(dh)

    def update_positions(self, fill):
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        self.current_positions[fill.symbol] += fill_dir*fill.quantity

    def update_holdings(self,fill):
        fill_dir = 0
        if fill.direction == 'BUY':
            fill_dir = 1
        if fill.direction == 'SELL':
            fill_dir = -1
        fill_cost = self.bars.get_latest_bars(fill.symbol)[0][5]  # Close price
        cost = fill_dir * fill_cost * fill.quantity
        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= (cost + fill.commission)
        
    def generate_naive_order(self,signal):
        order = None
            
        symbol = signal.symbol
        direction = signal.signal_type
        strength = 1.05
            
        market_quantity = floor(100 * strength)
        current_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and current_quantity == 0:
            order = OrderEvent(symbol, order_type, market_quantity, 'BUY')
        if direction == 'SHORT' and current_quantity == 0:
            order = OrderEvent(symbol, order_type, market_quantity, 'SELL')
        if direction == 'EXIT' and current_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(current_quantity), 'SELL')
        if direction == 'EXIT' and current_quantity < 0 :
            order = OrderEvent(symbol, order_type, abs(current_quantity), 'BUY')
        print `order`
        return order
        
    def update_signal(self,event):
        if event.type == 'SIGNAL':
            order_event = self.generate_naive_order(event)
            self.events.put(order_event)
        
    def create_equity_curve_dataframe(self):
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace = True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        self.equity_curve = curve
        
    def output_summary_stats(self):
        total_return = self.equity_curve['equity_cure'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns)
        max_drawdown, drawdown_duration = create_drawdowns(pnl)

        stats = [('Total Returns', '%0.2f%%' % ((total_return - 1.0) * 100.0)),
                  ('Sharpe Ratio', '%0.2f' % sharpe_ratio),
                  ('Max Drawdown', '%0.2f%%' % (max_drawdown * 100.0)),
                  ('Drawdown Duration', '%d' % drawdown_duration)]
        return stats