import Queue
import os
import time

import data
import event
import portfolio
import strategy
import execution

symbols = ['AAPL','CALD']
csv_path = os.path.join(os.getcwd(),'database')

Events = Queue.Queue()

Broker = execution.BasicExecution(events = Events)
DataFrame = data.HistoricalCSVData(events = Events, csv_path = csv_path, symbols = symbols)
Portfolio = portfolio.NaivePortfolio(bars = DataFrame, events = Events, start_date = '3-5-2018')
Strategy = strategy.BuyAndHoldStrategy(bars = DataFrame, events = Events)

while True:
    if DataFrame.continue_backtest == True:
        DataFrame.update_bars()
    else:
        break
    
    while True:
        try:
            event = Events.get(False)
        except Queue.Empty:
            break
        
        if event is not None:
            if event.type == 'MARKET':
                Strategy.calculate_signals(event)
                Portfolio.update_timeindex(event)
            elif event.type == 'SIGNAL':
                Portfolio.update_signal(event)
            elif event.type == 'ORDER':
                Broker.execute_order(event)
            elif event.type == 'FILL':
                Portfolio.update_fill(event)
