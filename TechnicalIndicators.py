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
import errno
import oandapy as opy

api = '0GSGYX7YU9H0UHHZ'
ti = TechIndicators(key=api, output_format='pandas')

def sma(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_sma(symbol, interval, time_period, series_type = 'close')
    return data
def ema(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_ema(symbol, interval, time_period, series_type = 'close')
    return data
def wma(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_wma(symbol, interval, time_period, series_type = 'close')
    return data
def dema(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_dema(symbol, interval, time_period, series_type = 'close')
    return data
def tema(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_tema(symbol, interval, time_period, series_type = 'close')
    return data
def trima(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_trima(symbol, interval, time_period, series_type = 'close')
    return data
def kama(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_kama(symbol, interval, time_period, series_type = 'close')
    return data
def mama(symbol, interval, time_period, series_type = 'close', fastlimit=None, slowlimit=None):
    data = ti.get_mama(symbol, interval, time_period, series_type = 'close', fastlimit=None, slowlimit=None)
    return data
def t3(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_t3(symbol, interval, time_period, series_type = 'close')
    return data
def macd(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, signalperiod=None):
    data = ti.get_macd(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, signalperiod=None)
    return data
def macdext(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, signalperiod=None, fastmatype=None, signalmatype=None):
    data = ti.get_macdext(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, signalperiod=None, fastmatype=None, signalmattype=None)
    return data
def stoch(symbol, interval, fastkperiod=None, slowkperiod=None, slowdperiod=None, slowkmatype=None, slowdmatype=None):
    data = ti.get_stoch(symbol, interval, fastkperiod=None, slowkperiod=None, slowdperiod=None, slowkmatype=None, slowdmatype=None)
    return data
def stochf(symbol, interval, fastkperiod=None, fastdperiod=None, fastdmatype=None):
    data = ti.get_stochf(symbol, interval, fastkperiod=None, fastdperiod=None, fastdmatype=None)
    return data
def rsi(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_rsi(symbol, interval, time_period, series_type = 'close')
    return data
def stochrsi(symbol, interval, time_period, series_type = 'close', fastkperiod=None, fastdperiod=None, fastdmatype=None):
    data = ti.get_stochrsi(symbol, interval, time_period, series_type = 'close', fastkperiod=None, fastdperiod=None, fastdmatype=None)
    return data
def willr(symbol, interval, time_period):
    data = ti.get_willr(symbol, interval, time_period)
    return data
def adx(symbol, interval, time_period):
    data = ti.get_adx(symbol, interval, time_period)
    return data
def adxr(symbol, interval, time_period):
    data = ti.get_adxr(symbol, interval, time_period)
    return data
def apo(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, matype=None):
    data = ti.get_apo(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, matype=None)
    return data
def ppo(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, matype=None):
    data = ti.get_ppo(symbol, interval, series_type = 'close', fastperiod=None, slowperiod=None, matype=None)
    return data
def mom(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_mom(symbol, interval, time_period, series_type = 'close')
    return data
def bop(symbol, interval, time_period):
    data = ti.get_bop(symbol, interval, time_period)
    return data
def cci(symbol, interval, time_period):
    data = ti.get_cci(symbol, interval, time_period)
    return data
def cmo(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_cmo(symbol, interval, time_period, series_type = 'close')
    return data
def roc(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_roc(symbol, interval, time_period, series_type = 'close')
    return data
def rocr(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_rocr(symbol, interval, time_period, series_type = 'close')
    return data
def aroon(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_aroon(symbol, interval, time_period, series_type = 'close')
    return data
def aroonosc(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_aroonosc(symbol, interval, time_period, series_type = 'close')
    return data
def mfi(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_mfi(symbol, interval, time_period, series_type = 'close')
    return data
def trix(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_trix(symbol, interval, time_period, series_type = 'close')
    return data
def ultsoc(symbol, interval, timeperiod1=None, timeperiod2=None, timeperiod3=None):
    data = ti.get_ultsoc(symbol, interval, timeperiod1=None, timeperiod2=None, timeperiod3=None)
    return data
def dx(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_dx(symbol, interval, time_period, series_type = 'close')
    return data
def minus_di(symbol, interval, time_period):
    data = ti.get_minus_di(symbol, interval, time_period)
    return data
def plus_di(symbol, interval, time_period):
    data = ti.get_plus_di(symbol, interval, time_period)
    return data
def minus_dm(symbol, interval, time_period):
    data = ti.get_minus_dm(symbol, interval, time_period)
    return data
def plus_dm(symbol, interval, time_period):
    data = ti.get_plus_dm(symbol, interval, time_period)
    return data
def bbands(symbol, interval, time_period,  series_type = 'close', nbdevup=None, nbdevdn=None, matype=None):
    data = ti.get_bbands(symbol, interval, time_period,  series_type = 'close', nbdevup=None, nbdevdn=None, matype=None)
    return data
def midpoint(symbol, interval, time_period, series_type = 'close'):
    data = ti.get_midpoint(symbol, interval, time_period, series_type = 'close')
    return data
def midprice(symbol, interval, time_period):
    data = ti.get_midprice(symbol, interval, time_period)
    return data
def sar(symbol, interval, acceleration=None, maximum=None):
    data = ti.get_sar(symbol, interval, acceleration=None, maximum=None)
    return data
def trange(symbol, interval):
    data = ti.get_trange(symbol, interval)
    return data
def atr(symbol, interval, time_period):
    data = ti.get_atr(symbol, interval, time_period)
    return data
def natr(symbol, interval, time_period):
    data = ti.get_natr(symbol, interval, time_period)
    return data
def ad(symbol, interval):
    data = ti.get_ad(symbol, interval)
    return data
def adosc(symbol, interval, fastperiod=None, slowperiod=None):
    data = ti.get_adosc(symbol, interval, fastperiod=None, slowperiod=None)
    return data
def obv(symbol, interval):
    data = ti.get_obv(symbol, interval)
    return data
def ht_trendline(symbol, interval, series_type = 'close'):
    data = ti.get_ht_trendline(symbol, interval, series_type = 'close')
    return data
def ht_sine(symbol, interval, series_type = 'close'):
    data = ti.get_ht_sine(symbol, interval, series_type = 'close')
    return data
def ht_trendmode(symbol, interval, series_type = 'close'):
    data = ti.get_ht_trendmode(symbol, interval, series_type = 'close')
    return data
def ht_dcperiod(symbol, interval, series_type = 'close'):
    data = ti.get_ht_dcperiod(symbol, interval, series_type = 'close')
    return data
def ht_dcphase(symbol, interval, series_type = 'close'):
    data = ti.get_ht_dcphase(symbol, interval, series_type = 'close')
    return data
def ht_phasor(symbol, interval, series_type = 'close'):
    data = ti.get_ht_phasor(symbol, interval, series_type = 'close')
    return data
