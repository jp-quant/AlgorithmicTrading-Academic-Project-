import numpy as np
import pandas as pd

#incorporate Sharpe Ratio, Maximum Drawdown and its Duration
#This is for the performance analysis of our backtest

def create_sharpe_ratio(returns, periods = 98280):

    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(equity_curve):

    hwm = [0]
    eq_idx = equity_curve.index
    drawdown = pd.Series(index = eq_idx)
    duration = pd.Series(index = eq_idx)

    for i in range(1,len(eq_idx)):
        cur_hwm = max(hwm[i-1],equity_curve[i])
        hwm.append(cur_hwm)
        drawdown[i] = hwm[i] - equity_curve[i]
        duration[i] = 0 if drawdown[i] == 0 else duration[i-1]
    return drawdown.max(), duration.max()