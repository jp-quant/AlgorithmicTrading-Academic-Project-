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
import oandapy as opy


class Portfolio:

    def __init__(self,
                 balance =  10000
                 ):
        self.balance = balance
        


