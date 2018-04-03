import datetime
import numpy as np
import pandas as pd
import Queue
from abc import ABCMeta, abstractmethod
from event import SignalEvent

class Strategy(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError('implement calculate_signals() to proceed')

class BuyAndHoldStrategy(Strategy):
    
    def __init__(self,bars,events):
        self.bars = bars
        self.symbols = self.bars.symbols
        self.events = events
        self.bought = self._calculate_initial_bought()

        
    def _calculate_initial_bought(self):
        bought = {}
        for i in self.symbols:
            bought[i] = False
        return bought
        
    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbols:
                bars = self.bars.get_latest_bars(s, N=1)
                if bars is not None and bars != []:
                    if self.bought[s] == False:
                        signal = SignalEvent(s, bars[0][1], 'LONG')
                        self.events.put(signal)
                        self.bought[s] = True

class SimpleSMACrossing(Strategy):
# for each new bar loaded, see if sma100 crossed sma200 using 4 data points from both
# condition to place trade: if the latest smas crossed but the previous data didn't
    def __init__(self,bars,events,portfolio):
        self.bars = bars
        self.symbols = self.bars.symbols
        self.events = events
        self.portfolio = portfolio
        self.current_positions = self.portfolio.current_positions

    def calculate_signals(self, event):
        if event.type == 'MARKET':
            for s in self.symbols:
                bars = self.bars.get_latest_bars(s, N=5)
                sma_difference = []
                negative_count = 0
                positive_count = 0
                for i in bars:
                    difference = i[-2] - i[-1] #sma100 - sma200
                    sma_difference.append(difference)
                if len(sma_difference) >= 5:
                    for x in range(5):
                        if sma_difference[x] < 0:
                            negative_count += 1
                        if sma_difference[x] > 0:
                            positive_count += 1
                    if negative_count >= 3 and positive_count >=1:
                        if sma_difference[0] < 0:
                            if self.current_positions[s] == 0:
                                signal = SignalEvent(s, bars[-1][1], 'LONG')
                                self.events.put(signal)
                            else:
                                signal = SignalEvent(s, bars[-1][1], 'EXIT')
                                self.events.put(signal)
                    if positive_count >= 3 and negative_count >=1:
                        if sma_difference[0] > 0:
                            if self.current_positions[s] == 0:
                                signal = SignalEvent(s, bars[-1][1], 'SHORT')
                                self.events.put(signal)
                            else:
                                signal = SignalEvent(s, bars[-1][1], 'EXIT')
                                self.events.put(signal)