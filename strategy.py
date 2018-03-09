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
