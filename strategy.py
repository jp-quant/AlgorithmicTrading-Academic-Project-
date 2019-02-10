import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import queue
import statsmodels.api as sm
from math import floor
from abc import ABCMeta, abstractmethod
from event import SignalEvent
from event import MarketEvent
from scipy.optimize import minimize
import talib

from nn_bbox import Stocks_BBox


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError('implement calculate_signals() to proceed')



class PortfolioSharpeMaximization(Strategy):

    # [Sample Strategy for Algorithmic Trading Program] - written by Jack P.
    # Utilize basic statistical techniques for portfolio management
    # STRATEGY BLUEPRINT
    '''
    The goal is to maximize our portfolio sharpe ratio, which comprises of a diversifying
    amount of stocks, and this is how we maximize our sharpe ratio:
    -- CALCULATE WEIGHTS FOR ALL TRADABLE ASSETS
    
    Portfolio's Sharpe Ratio = (Portfolio's Expected Return - Risk Free Rate)/Portfolio's Return STD

    The equation above is the main one that we need, the fundamental value of invesments
    Portfolio's Expected Return = E(R) = sum of assets expected returns times the allocation weight

    Portfolio's Return STD = STD(R) = square root of its variance
    Var(R) = sum of covariances times the two weights in which the covariance measured to

    As we can see, the only input variable need is the logarithmic returns of all assets
    at a certain lookback time (at the tail of our data)

    '''

    def __init__(self,bars,events,portfolio):
        self.bars = bars
        self.symbols = self.bars.symbols
        self.events = events
        self.portfolio = portfolio


    def calculate_signals(self, event):
        if event.type == 'MARKET':
            all_signals = []
            #----CHECK AND MODIFY EXISTING POSITIONS
            #----CONSTANTLY OPTIMIZING ALLOCATIONS AT 50% OF TOTAL PORTFOLIO VALUE
            allocations_signals = self.allocations_optimization_signals(event,self.symbols,'full')
            for s in allocations_signals:
                all_signals.append(s)
            #----PUT ALL SIGNALS INTO QUEUE----#
            if len(all_signals) != 0:
                for s in all_signals:
                    self.events.put(s)
            #----------------------------------#

    def allocations_optimization_signals(self,event,symbols,mode,allocations_pct=1,tail_count=None):
        # WE UPDATE ASSETS_ALLOCATIONS EVERYTIME WE DO FULL OPTIMIZATIONS
        allocations_plan = self.calculate_allocations_plan(event,symbols,mode,allocations_pct,tail_count)
        # ALLOCATIONS PLAN CREATED CONTAINS FRACTIONAL SHARE ALLOCATIONS
        signals = []
        buying_power = self.portfolio.cash_balance
        # we'll start with cash balance as the buying power
        # this will adjust as we adjust positions (hypothetically)
        for s in symbols:
            # First check if we can get back any buying power by selling part of our shares
            if allocations_plan.current_positions[s] > allocations_plan.share_allocations[s]:
                action = 'SELL'
                shares = abs(allocations_plan.share_allocations[s]-allocations_plan.current_positions[s])
                # since we're selling n shares, we're getting n*close of the assets back as buying power
                buying_power += shares*allocations_plan.closes[s]
                if (shares == 0) or (action == None):
                    pass
                else:
                    signals.append(SignalEvent(s,shares = shares,action = action, order_type = 'MARKET',
                                                stamp = event.stamp))
        for s in symbols:
            # Now we supposedly have an atleast equal or higher amount of buying power due to adjustment we'll do everything else
            if buying_power < abs(allocations_plan.value_allocations[s]):
                action = 0
                shares = 0
            elif allocations_plan.current_positions[s] < allocations_plan.share_allocations[s]:
                action = 'BUY'
                shares = abs(allocations_plan.share_allocations[s]-allocations_plan.current_positions[s])
            else:
                action = None
                shares = 0
            if (shares == 0) or (action == None):
                pass
            else:
                signals.append(SignalEvent(s,shares = shares,action = action, order_type = 'MARKET',
                                            stamp = event.stamp))
        return signals

    def calculate_allocations_plan(self,event,symbols,mode,allocations_pct=1,tail_count=None):
        result = pd.DataFrame()
        allocations = (self.calculate_optimal_allocations(symbols=symbols,mode=mode,tail_count=tail_count).loc[symbols])
        close = pd.Series(data = 0.0, index = symbols)
        value = pd.Series(data = 0.0, index = symbols)
        position = pd.Series(data = 0.0, index = symbols)
        current_portfolio_value = self.portfolio.cash_balance
        for s in symbols:
            current_portfolio_value += self.portfolio.holdings[s].at[event.stamp,'value']
            close[s] = self.portfolio.holdings[s].at[event.stamp,'close']
            value[s] = self.portfolio.holdings[s].at[event.stamp,'value']
            position[s] = self.portfolio.holdings[s].at[event.stamp,'position']
        value_allocations = (allocations_pct*current_portfolio_value*allocations['LONG']).round(6)
        result['value_allocations'] = value_allocations
        result['closes'] = close
        result['share_allocations'] = np.floor(result['value_allocations']/result['closes'])
        result['current_values'] = value
        result['current_positions'] = position
        return result

    #---------------------------------PORTFOLIO OPTIMIZATION--------------------------------#
    #------all functions below are used for finding optimal allocations for our assets------#

    def calculate_optimal_allocations(self,symbols,mode,tail_count=None):
        # USING SCIPY.OPTIMIZE'S MINIMIZE() FUNCTION TO OBTAIN OPTIMAL allocations and positions for latest trends
        cons = ({'type':'eq','fun':self.check_sum})
        bounds = []
        init_guess = []
        log_ret = {}
        for s in symbols:
            bounds.append((0,1))
            init_guess.append(1/len(symbols))
        if mode == 'tail':
            try:
                for s in symbols:
                    df = self.bars.latest_symbol_data[s].tail(tail_count)
                    log_ret[s] = np.log(df.close/df.close.shift(1)).dropna()
            except TypeError:
                print('Tail count needs to be an integer.')
        elif mode == 'full':
            for s in symbols:
                df = self.bars.latest_symbol_data[s]
                log_ret[s] = np.log(df.close/df.close.shift(1)).dropna()
        log_ret = pd.DataFrame(log_ret)    
        max_sharpe = minimize(self.neg_sharpe,
                            x0=init_guess,
                            args=log_ret,
                            method='SLSQP',
                            bounds = bounds,
                            constraints = cons)
        long_rvs = self.sharpe_report(list(max_sharpe.x),log_ret=log_ret)
        long_allocations = pd.Series(data=max_sharpe.x,index=symbols)
        result = pd.DataFrame()
        result['LONG'] = long_allocations.append(long_rvs)
        return result


    # minimize negative sharpe = maximizing positive sharpe
    def neg_sharpe(self,allocations,log_ret):
        return self.sharpe_report(allocations,log_ret)[2] * (-1)
    
    #constraint
    def check_sum(self,allocations):
        return (np.sum(allocations) - 1)
    
    def sharpe_report(self,allocations,log_ret): 

        # Can be used for multiple purposes
        # The function takes in the log returns of allocated asset values
        # and return the sharpe report for it

        weights = np.array(allocations)
        returns = np.sum(log_ret.mean() * weights)
        volatility = np.sqrt(np.dot(weights.T,np.dot(log_ret.cov(),weights)))
        sharpe_ratio = returns/volatility
        return pd.Series(data = [returns,volatility,sharpe_ratio],index = ['returns','volatility','sharpe'])
    #--------------------------------------------------------------------------------------#
