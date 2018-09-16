import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import matplotlib.pyplot as plt

ts = TimeSeries(key='0GSGYX7YU9H0UHHZ', output_format = 'pandas')
ti = TechIndicators(key='0GSGYX7YU9H0UHHZ', output_format='pandas')


