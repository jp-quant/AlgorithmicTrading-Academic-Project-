import datetime
import numpy as np
import pandas as pd
import queue
from abc import ABCMeta, abstractmethod
from event import SignalEvent
import statsmodels.api as sm #HPFilter
from statsmodels.tsa.seasonal import seasonal_decompose #ETS
from statsmodels.tsa.stattools import adfuller #unit root test for stationarity
from scipy.optimize import minimize


class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError('implement calculate_signals() to proceed')

##----------------------------------------------------
## SAMPLE STRATEGY (Portfolio Optimization + Trending Analysis)
##----------------------------------------------------
class SampleStrategy(Strategy):

    def __init__(self,bars,events,portfolio):
        self.bars = bars
        self.symbols = self.bars.symbols
        self.events = events
        self.portfolio = portfolio
        #if a strategy involves any technical indicators, you need to modify the dataframe
        #for this, I will add more data into the dataframe through initilize calculations
        self.periods = [5,8,13] # for MA calculations
        # DATA TO ADD = SMA, EWMA, DAILY RETURNS (ARITH AND LOG), DIFFERENCING (1ST AND 2ND ORDER)
        self.bars.add_data(self.symbols,periods=self.periods,sma=True,ewma=True,
                            arith_ret=True,log_ret=True,d1close=True,d2close=True)
        self.assets_allocations = pd.DataFrame(columns=self.symbols)
        self.market_daily_rvs = {}  # set daily returns and volatility/risk limits for each assets to track
        for s in self.symbols:
            self.market_daily_rvs[s] = pd.DataFrame(columns=['returns','volatility','sharpe'])



    def calculate_signals(self, event):
        if event.type == 'MARKET':
            # IF CURRENT STAMP DATE == START DATE: DO NOTHIN!
            if datetime.datetime.strptime(event.stamp,'%Y-%m-%d %H:%M:%S').date() == datetime.datetime.strptime(self.bars.latest_stamps[0],'%Y-%m-%d %H:%M:%S').date():
                for s in self.symbols:
                    signal = SignalEvent(s,event.stamp,None,0)
                    self.events.put(signal)
            # ONCE ABOVE STATEMENT IS FALSE: START CALCULATIONS
            else:
                # IF START OF A NEW DAY, PERFORM SIGNALS CALCULATIONS FOR START OF THE DAY
                if (datetime.datetime.strptime(self.bars.latest_stamps[-1],'%Y-%m-%d %H:%M:%S').date() != datetime.datetime.strptime(self.bars.latest_stamps[-2],'%Y-%m-%d %H:%M:%S').date()):
                    # AT THE START OF EVERYDAY, WE PERFORM FULL ALLOCATIONS ANALYSIS (BASE ON DAILY RETURNS SINCE START DAY)
                    signals = self.full_allocations_optimization_signals(event)
                    # UPDATE NECESSARY DATA FOR TODAY'S TRADING
                    self.update_daily_rvs(event)
                    #----[IN PROGRESS]
                    for s in signals:
                        self.events.put(s)
                # IN PROGRESS...[DO NOTHING ATM]
                else:
                    for s in self.symbols:
                        signal = SignalEvent(s,event.stamp,None,0)
                        self.events.put(signal)

    def full_allocations_optimization_signals(self,event):
        # WE UPDATE ASSETS_ALLOCATIONS EVERYTIME WE DO FULL OPTIMIZATIONS
        allocations = (self.calculate_optimal_allocations(mode='full').loc[self.symbols])/2
        current_portfolio_value = self.portfolio.cash_balance
        for s in self.symbols:
            current_portfolio_value += self.portfolio.current_holdings[s]['value']
        value_allocations = (current_portfolio_value*allocations.sum(axis=1)).round(6)
        signals = []
        for s in self.symbols:
            current_close = self.portfolio.current_holdings[s]['close']
            current_value = self.portfolio.current_holdings[s]['value']
            if current_value < value_allocations[s]:
                action = 'BUY'
                quantity = round(abs((value_allocations[s] - current_value)/current_close),6)
            elif current_value > value_allocations[s]:
                action = 'SELL'
                quantity = round(abs((current_value - value_allocations[s])/current_close),6)
            else:
                action = None
                quantity = 0
            signals.append(SignalEvent(s,event.stamp,action,quantity))
        return signals


    def tail_optimal_allocations_signals(self,event,tail_count=90):
        # calculate optimal allocations for assets trading and generate signals for portfolio to change
        allocations = self.calculate_optimal_allocations(mode='tail',tail_count=tail_count)
        current_portfolio_value = self.portfolio.cash_balance
        for s in self.symbols:
            current_portfolio_value += self.portfolio.current_holdings[s]['value']
        value_allocations = (current_portfolio_value*allocations.sum(axis=1)).round(6)
        signals = []
        for s in self.symbols:
            current_close = self.portfolio.current_holdings[s]['close']
            current_value = self.portfolio.current_holdings[s]['value']
            if current_value < value_allocations[s]:
                action = 'BUY'
                quantity = round(abs((value_allocations[s] - current_value)/current_close),6)
            elif current_value > value_allocations[s]:
                action = 'SELL'
                quantity = round(abs((current_value - value_allocations[s])/current_close),6)
            else:
                action = None
                quantity = 0
            signals.append(SignalEvent(s,event.stamp,action,quantity))
        return signals
    
    def generate_buy_and_hold_signal(self,s):
        bar = self.bars.get_latest_bars(s, N=1)
        quantity = (self.portfolio.initial_balance/len(self.symbols))/bar[-1]['close']
        if bar is not None and bar != []:
            stamp = bar[-1].name
            if self.portfolio.current_holdings[s]['position'] == 0:
                signal = SignalEvent(s, stamp, action = 'BUY',quantity = quantity)
            else:
                signal = SignalEvent(s,stamp,None,0)
            return signal


#---------------------------------PORTFOLIO OPTIMIZATION--------------------------------#
#------------all functions below are used for finding optimal allocations for our assets------------#

# INSPIRED SOURCE: http://bit.ly/2NYwHvD


    # RUN THIS FUNCTION BY ITSELF TO FIND OPTIMAL ALLOCATIONS THROUGH MATHEMATICAL CALCULATIONS
    # This is a much faster and efficient way to optimize time and efficiency
    def calculate_optimal_allocations(self,mode,tail_count=None):
        # USING SCIPY.OPTIMIZE'S MINIMIZE() FUNCTION TO OBTAIN OPTIMAL allocations and positions for latest trends
        cons = ({'type':'eq','fun':self.check_sum})
        bounds = []
        init_guess = []
        log_ret = {}
        for s in self.symbols:
            bounds.append((0,1))
            init_guess.append(1/len(self.symbols))
        if mode == 'tail':
            try:
                for s in self.symbols:
                    log_ret[s] = pd.DataFrame(self.bars.latest_symbol_data[s]).tail(tail_count).log_ret
            except TypeError:
                print('Tail count needs to be an integer.')
        elif mode == 'last_day':
            stamps = self.portfolio.daily_logged_stamps[-1]
            for s in self.symbols:
                log_ret[s] = pd.DataFrame(self.bars.latest_symbol_data[s]).loc[stamps].log_ret
        elif mode == 'full':
            for s in self.symbols:
                log_ret[s] = pd.DataFrame(self.bars.latest_symbol_data[s]).log_ret
        elif mode == 'position_value':
            for s in self.symbols:
                log_ret[s] = self.position_value_ts(s)
        log_ret = pd.DataFrame(log_ret)    
        max_sharpe = minimize(self.neg_sharpe,
                            x0=init_guess,
                            args=log_ret,
                            method='SLSQP',
                            bounds = bounds,
                            constraints = cons)
        min_sharpe = minimize(self.pos_sharpe,
                            x0=init_guess,
                            args=log_ret,
                            method='SLSQP',
                            bounds = bounds,
                            constraints = cons)
        long_rvs = self.ret_vol_sharpe(list(max_sharpe.x),log_ret=log_ret)
        short_rvs = self.ret_vol_sharpe(list(min_sharpe.x),log_ret=log_ret)
        long_allocations = pd.Series(data=max_sharpe.x,index=self.symbols)
        short_allocations = pd.Series(data=min_sharpe.x,index=self.symbols)*(-1)
        result = pd.DataFrame()
        result['LONG'] = long_allocations.append(long_rvs)
        result['SHORT'] = short_allocations.append(short_rvs)
        return result


# <<-----------------| FUNCTIONS USED FOR ALLOCATIONS CALCULATION |----------------->>

    # minimize positive sharpe = maximizing negative sharpe
    def pos_sharpe(self,allocations,log_ret):
        return self.ret_vol_sharpe(allocations,log_ret)[2]
    # minimize negative sharpe = maximizing positive sharpe
    def neg_sharpe(self,allocations,log_ret):
        return self.ret_vol_sharpe(allocations,log_ret)[2] * (-1)

    # minimizing volatility = efficient frontier (set of optimal portfolio with minimal risk)
    
    #constraint
    def check_sum(self,allocations):
        return (np.sum(allocations) - 1)


    def ret_vol_sharpe(self,allocations,log_ret): # use minimize() to apply to any value retuns
        # take assigned allocations for all assets and their concatenated logarithmic returns for each specified time frame
        # allow us to place different positions for different assets 
        # return list: [returns, volatility, sharpe ratio]
        if len(allocations) != len(self.symbols):
            print('Length of allocations needs to be equal to length of symbols assigned')
        else:
            if type(log_ret) != pd.DataFrame:
                print('log_ret needs to be a return dataframe of all allocated symbols')
            else:
                weights = np.array(allocations)
                returns = np.sum(log_ret.mean() * weights) * len(log_ret)
                volatility = np.sqrt(np.dot(weights.T,np.dot(log_ret.cov()*len(log_ret),weights)))
                sharpe_ratio = returns/volatility
                return pd.Series(data = [returns,volatility,sharpe_ratio],index = ['returns','volatility','sharpe'])


# <<-------| SIMULATE OPTIMAL ALLOCATIONS |------->>
#                (OPTIONAL SECTION)

    # RUN THIS FUNCTION BY ITSELF TO FIND OPTIMAL ALLOCATIONS THROUGH SIMULATIONS
    # This is much less efficient compared to mathemtical way above but much easier to understand
    def simulate_optimal_allocations(self,mode,tail_count=None,simulations_count=1000):
        # run simulations to find best allocation ratio for all assets
        # using logarithmic returns and data that's constantly being updated
        # return allocations with the highest sharpe ratio (each minute)
        trials = simulations_count #amount of time we will run our simulation
        all_weights = np.zeros((trials,len(self.symbols)))
        returns = np.zeros(trials)
        volatility = np.zeros(trials)
        sharpe_ratio = np.zeros(trials)
        log_ret = {}
        if mode == 'tail':
            try:
                for s in self.symbols:
                    log_ret[s] = pd.DataFrame(self.bars.latest_symbol_data[s]).tail(tail_count).log_ret
            except TypeError:
                print('Tail count needs to be an integer.')
        elif mode == 'daily':
            stamps = self.portfolio.daily_logged_stamps[-1]
            for s in self.symbols:
                log_ret[s] = pd.DataFrame(self.bars.latest_symbol_data[s]).loc[stamps].log_ret
        elif mode == 'full':
            for s in self.symbols:
                log_ret[s] = pd.DataFrame(self.bars.latest_symbol_data[s]).log_ret
        log_ret = pd.DataFrame(log_ret)
        np.random.seed(simulations_count) 
        for t in range(trials):
            weights = np.array(np.random.random(len(log_ret.columns)))
            weights = weights/np.sum(weights)
            all_weights[t,:] = weights
            returns[t] = np.sum(log_ret.mean() * weights) * len(log_ret)
            volatility[t] = np.sqrt(np.dot(weights.T,np.dot(log_ret.cov()*len(log_ret),weights)))
            sharpe_ratio[t] = returns[t]/volatility[t]
        
        buy_rvs = pd.Series(data = [returns[sharpe_ratio.argmax()],
                                    volatility[sharpe_ratio.argmax()],
                                    sharpe_ratio.max()],index = ['returns','volatility','sharpe'])
        sell_rvs = pd.Series(data = [returns[sharpe_ratio.argmin()],
                                    volatility[sharpe_ratio.argmin()],
                                    sharpe_ratio.min()],index = ['returns','volatility','sharpe'])
        buy_allocations = pd.Series(data=all_weights[sharpe_ratio.argmax(),:],
                                                    index=self.symbols)
        sell_allocations = pd.Series(data=all_weights[sharpe_ratio.argmin(),:],
                                                    index=self.symbols)
        result = pd.DataFrame()
        result['LONG'] = buy_allocations.append(buy_rvs)
        result['SHORT'] = sell_allocations.append(sell_rvs)
        return(result)


#----------------------------------MARKET ANALYSIS-------------------------------------#
#-------THIS IS WHERE WE WILL PERFORM MARKET ANALYSIS AND PLAY WITH PROBABILITIES------#
# ------[IN PROGRESS] -> ARIMA & SEASONAL ARIMA MODELING


    def hp_trend_analysis(self,symbol):
        trends = self.hp_trend_report(symbol)
        



    def intraday_positions_adjustments(self,event):
        # LOOK FOR POTENTIAL OPTIMAL ALLOCATIONS ADJUSTMENTS WITHIN THE DAY
        # BASE ON MARKET'S VOLATILITY/RISK AND ASSETS' INVESTMENT RETURNS
        # [IN PROGRESS]
        for s in self.symbols:
            pos_value = self.position_value_ts(s)
            rvs = self.market_daily_rvs[s]


    # RETURN CURRENT ASSET'S POSITION TIMESERIES, START WHERE WE FIRST ASSIGNED POSITION VALUE
    def position_value_ts(self,symbol):
        record = self.portfolio.all_holdings[symbol]
        current_position = self.portfolio.current_holdings[symbol]['position']
        for i in range(-1,(-len(record)-1),-1): #going backwards
            indexed_position = record.loc[record.index[i]]['position']
            if indexed_position == current_position:
                pass
            elif indexed_position != current_position:
                start_stamp = record.index[i+1]
                break
        position_value_ts = record.loc[record.index[record.index.get_loc(start_stamp):]]
        return position_value_ts.round(6)


    def update_daily_rvs(self,event):
        # RECORD PREVIOUS DAY'S RET, VOL AND SHARPE VALUES
        stamps = self.portfolio.daily_logged_stamps[-1] # previous day stamps
        ind = datetime.datetime.strptime(stamps[-1],'%Y-%m-%d %H:%M:%S').date()
        for s in self.symbols:
            df = pd.DataFrame(self.bars.latest_symbol_data[s]).loc[stamps].log_ret
            exp_ret = df.mean()*len(df)
            exp_vol = df.std()*len(df)
            sharpe = exp_ret/exp_vol
            self.market_daily_rvs[s] = self.market_daily_rvs[s].append(pd.Series(data=[exp_ret,exp_vol,sharpe],
                                                        index=['returns','volatility','sharpe'],
                                                        name=ind))



    def hp_trend_report(self,dataframe):
        # categorize trend in ordered time using HP Filter's derivative (dtrend (delta trend))
        # RETURN: Sequential list of trends with respect to time
        #         Each element contains: [direction, extracted dataframe based on trend's index (this will be used for multiple other purposes)]
        # IMPORTANT: THIS CAN ONLY BE APPLIED TO STATIC DATAFRAME, USE FOR HISTORICAL DATA ANALYSIS
        #            WITH ABSOLUTE LOOK-AHEAD BIAS. RECOMMEND TO USE PERIODICALLY (DAILY, HOURLY, ETC)
        hpfilter = sm.tsa.filters.hpfilter(dataframe.close)
        hp_trend = hpfilter[1]
        hp_noise = hpfilter[0]
        result = pd.DataFrame().append(dataframe)
        result['hptrend'] = hp_trend
        result['hpnoise'] = hp_noise
        dtrend = ((hp_trend/hp_trend.shift(1))-1).dropna()
        start = 0
        record = []
        track = []
        while len(track) != len(dtrend.index):
            if dtrend[start] < 0:
                down = (dtrend < 0)
                indexes = []
                for i in range(start,len(down)):
                    if down[i] == True:
                        track.append(i)
                        indexes.append(down.index[i])
                        if i == range(len(down))[-1]: #if we reach last value
                            record.append(['DOWN',result.loc[pd.Index(indexes)]])
                            break
                    elif down[i] == False:
                        start = i
                        record.append(['DOWN',result.loc[pd.Index(indexes)]])
                        break
            elif dtrend[start] > 0:
                up = (dtrend > 0)
                indexes = []
                for i in range(start,len(up)):
                    if up[i] == True:
                        track.append(i)
                        indexes.append(up.index[i])
                        if i == range(len(up))[-1]: #if we reach last value
                            record.append(['UP',result.loc[pd.Index(indexes)]])
                            break
                    elif up[i] == False:
                        start = i
                        record.append(['UP',result.loc[pd.Index(indexes)]])
                        break
            elif dtrend[start] == 0:
                still = (dtrend == 0)
                indexes = []
                for i in range(start,len(still)):
                    if still[i] == True:
                        track.append(i)
                        indexes.append(still.index[i])
                        if i == range(len(still))[-1]: #if we reach last value
                            record.append(['STILL',result.loc[pd.Index(indexes)]])
                            break
                    elif still[i] == False:
                        start = i
                        record.append(['STILL',result.loc[pd.Index(indexes)]])
                        break
        return record