
# Algorithmic Trading Program


## Table of Contents
 - [Introduction](https://github.com/xphysics/AlgorithmicTrading#introduction)
 - [Features Log](https://github.com/xphysics/AlgorithmicTrading#features-log)
 - [General Blueprint](https://github.com/xphysics/AlgorithmicTrading#blueprint)
 - [Components Breakdown/How-To-Use](https://github.com/xphysics/AlgorithmicTrading#components-breakdownhow-to-use)
   - [backtest.py](https://github.com/xphysics/AlgorithmicTrading#1-backtestpy---run-to-start-backtesting-process)
   - [event.py](https://github.com/xphysics/AlgorithmicTrading#2-eventpy)
   - [broker.py](https://github.com/xphysics/AlgorithmicTrading#3-brokerpy)
   - [COMING SOON...]

## Introduction
Algorithmic trading allows individuals to rid fundamental and psychological hunches, or guessings, when trading any financial markets, stocks, bonds, forex, options, etc. With the extensive and flexible event-driven structure of this project, users can craft new customary components, such as portfolio, dataframe or algo strategies, and implement them to backtest on any desired market, as long as time series data is available. This program is an ongoing and continuously improving database, with potentially endless implementations to be added.

## Features Log
 - Only focus on backtesting engine first, live trading will be implemented in the future with more updated Broker
 - Only download and update stocks by using included AlphaVantage API Key (no options, forex, etc yet)
 - If you have csv data on other markets to backtest on, feel free to incorporate it.
 - *Current Strategy*: Daily portfolio allocations optimizations through maximizing sharpe ratio across all holdings

## General Blueprint
Our engine is structured to be an event-driven system. Although slower than vectorised backtesting structure, by doing this, in addition to ridding psychological hunches and guessing, written codes can be recycled to adapt to live trading in the future. Components are listed sequentially below, ascending from most basic to complex. As each component inherits the ones above, the last component, Strategy, is where most quantitative work reside.

1. **EVENT:** This is the simplest yet key component in our engine. Due to the nature of event-driven structure, we require a fundamental class that could identify what action to proceed taking in an event loop. There are different event types, noted in event.py: MarketEvent, SignalEvent, OrderEvent, FillEvent.

3. **BROKER:** A broker is essential to perform any trade. At the moment, we are focusing on developing a solid backtesting engine before moving on to livetrading. Therefore, our current Broker component is extremely simple as it is purely responsible for fulfilling order requested by our Portfolio component. It will then place a FillEvent to notify out Portfolio that the order has been executed so we could update our portfolio. 

5. **DATAFRAME:**  First of important components, we need a dataframe that contains all data for portfolio and strategy to use. At the moment, our CSVHistoricalDataFrame is the only one existed as its being tailored to adapt to Strategy and Portfolio's backtesting needs, such as adding additional calculated data on top of market OHCLV data, logging backtesting progresses, or data categorizations.

7. **PORTFOLIO:** It being on the ladder of importance, we need a portfolio management class that handles the order and logic of positions being placed, current and subsequents. Portfolio will keep track of each asset value and positions, along with updating them after orders are executed. Information of portfolio value and assets allocations are essential to optimize our portfolio as much as possible. NOTE: Portfolio optimization can be placed in either Portfolio or Strategy, but preferrably Strategy, as it being the most important component, thus having access to ALL other components, including our Portfolio.

9. **STRATEGY:** This is where most high-end quantitative contents reside. Strategy inherits all the classes/components above, as it can observe and capture latest financial data having access to our DataFrame, on top of montoring our portfolio. Calculations performed periodically during trading can all be made in this most valuable component. 

The goal of trading financial markets quantitatively is to continuously perform necessary calculations and adjustments in position sizings, allocations, market predictions and risk management through market analysis, etc. This imply the majority of quantitative decision making and calculations reside within Strategy & Portfolio components. Future live testing implementations will require major updates on the Broker component.

##  Components Breakdown/How-To-Use
#### Getting Started
- If you do not have Python 3.7, download it [here](https://www.python.org/downloads/release/python-370/ "here").
- In terminal, navigate to project directory and type `pip install -r requirements.txt` to install all required modules for usage.

------------

#### 1. BACKTEST.PY - (Run to start backtesting process)
After importing all necessary components and requirement modules, we will first set our `symbols` to trade, and `csv_path` to upload financial data and update if necessary.
```python
# symbols in list form with each asset name in string
symbols=['AAPL', 'GOOG', 'AMZN', 'NVDA', 'TSLA', 'NFLX', 'FB' ,'AMD', 'CSCO', 'INTC']
# define our csv path by joining current path (project's folder) and database
csv_path=os.path.join(os.getcwd(),'database')
```
Next up, we will initialize all of our components (more extensive details on codes later).
```python
Events = queue.Queue() #event-driven queueing system
Broker = broker.BasicBroker(events = Events)
DataFrame = data.CSVData(events = Events, csv_path = csv_path, symbols = symbols)
Portfolio = portfolio.SamplePortfolio(bars = DataFrame, events = Events)
Strategy = strategy.SampleStrategy(bars = DataFrame, events = Events, portfolio = Portfolio)
```
Now that everything is successfully initialized, we will start our backtesting process . Keep in mind you do not have to know the specifics at the moment of each method called, but rather focus on their functionalities and what they do. Their detailed explanations will be shown later.
```python
'''--------------------------------DESCRIPTION----------------------------------
OUTER LOOP: First we start updating our historical data from the database
            onto ourDataFrame. This is equivalent to a new bar popping
            up on your ticker chart. After the method is called, DataFrame
            will automatically place a MarketEvent into our event queue.
            This will be retreived firstly in our inner loop to process the
            newest data.
INNER LOOP: Start by retreiving the first event in our event queue, which is
            the MarketEvent placed from the outer loop. Portfolio and
            Strategy will then retreive MarketEvent with a stamp to update
            portfolio timestamp and calculate possible signals to generate
            SignalEvents to place into queue. This process continues on as
            SignalEvent would be passed on to Portfolio to generate an
            OrderEvent to be placed in queued. This OrderEvent will then
            be received by our Broker to fulfill the order. After the order
            is fulfilled, the Broker will place a FillEvent into the queue.
            This event queue will be retreived again by our portfolio.
            Portfolio will then update necessary informations such as
            assets values, positions, portfolio values, etc.
            This loop will continues on until all necessary performances
            are executed. This will prompts the Queue.empty to break
            out of the inner loop to return to the outer loop to update
            more bars.
This goes on until all bars are updated and backtest is complete.
---------------------------------------------------------------------------------------'''
#------OUTER LOOP------#
while True:
	if DataFrame.continue_backtest == True:
  		DataFrame.update_bars()
	else:
	 	break
#-------INNER LOOP-------#
	while True:
		try:
			event = Events.get(False)
		except queue.Empty:
			break

		if event is not None:
			if event.type == 'MARKET':
				Portfolio.update_market(event) 
				Strategy.calculate_signals(event)
			elif event.type == 'SIGNAL':
				Portfolio.update_signal(event)
			elif event.type == 'ORDER':
				Broker.execute_order(event)
			elif event.type == 'FILL':
				Portfolio.update_portfolio(event)
```
#### 2. EVENT.PY
As an event-driven backtesting engine, we require an Event class that creates and identifies different event queues.
There are 4 different events to be identified by our components.

 - **MarketEvent**: placed in queue by DataFrame as soon as new bars have been updated. The event only needs to contain the timestamp which signifies the latest bars' timestamp. Retreived by Portfolio to update its current holdings and values reflected by the new prices. Strategy will also retreive it to calculate potential signals to be placed in queue.
	
```python
class MarketEvent:

    def __init__(self, stamp):
        self.type = 'MARKET'
        self.stamp = stamp
```
 - **SignalEvent**: placed in queue by Strategy after it performed necessary calculations needed after the latest bars are updated. This will thus be retreived by Portfolio to generate orders. The event needs to contain information needed to generate orders, including the timestamp, symbol, action and quantity. Meaning that each asset has its own event rotation queue as our engine will iterate through all of desired assets to trade.
```python     
class SignalEvent:

    def __init__(self,symbol,stamp,action = None,quantity = None):
        self.type = 'SIGNAL'
        self.symbol = symbol
        self.stamp = stamp
        self.action = action # BUY, SELL, EXIT
        self.quantity = quantity
```
 - **OrderEvent**: placed in queue by Portfolio after it retreived the SignalEvent. Portfolio will then generate the order necessary and place them into queue as OrderEvents, which will be retreived by our Broker to execute the trade. OrderEvent therefore must include informations for the Broker to perform its task. We also configure the way OrderEvent will be printed whenever called necessary.
```python
class OrderEvent:

    def __init__(self,symbol,stamp,order_type,quantity):
        self.type = 'ORDER'
        self.symbol = symbol
        self.quantity = quantity
        self.order_type = order_type
        self.stamp = stamp

    def __repr__(self):
        return "ORDER --> Symbol=%s, Type=%s, Quantity=%s TimeStamp= %s " % (self.symbol, self.order_type, self.quantity, self.stamp)
```
 - **FillEvent**: placed in queue by Broker after the order(s) desired have been executed. This FillEvent will be retreived by our Portfolio to update all holdings trackings and portfolio values, again, reflected by the changes made through the orders that were placed.
```python
class FillEvent:
    def __init__(self,stamp,symbol,exchange,
                quantity,order_type,commission=None):
                self.type = 'FILL'
                self.stamp = stamp
                self.symbol = symbol
                self.exchange = exchange
                self.quantity = quantity
                self.order_type = order_type

                if commission is None:
                    self.commission = self.calculate_ib_commission()
                else:
                    self.commission = commission

    def calculate_ib_commission(self):
    # OPTIONAL FOR NOW: OUR CURRENT MODEL JUST ASSUME NO COMMISSION REQUIRED FOR SIMPLICITY
            return 1.3
```
#### 3. BROKER.PY
At the moment, our broker class is fairly simple as it will be responsible for "executing" orders, basically taking in OrderEvents and placing FillEvents into queue.
First, we'll define a general Broker class to enforce abstract method(s) to be implemented and called. We'll also do this for other components as well. This is to enforce the general blueprint of how our backtesting engine work, therefore any new versions created (ex: Live Trading Broker) will also have to contain those required methods.
```python
class Broker(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        raise NotImplementedError('Implement execute_order before proceeding')
```
Now that we have our execute_order() defined as an abstract method. We will proceed to make any broker we want, inherting the general Broker class we just created. In this case, we will create our BasicBroker with the abstract method.
```python
class BasicBroker(Broker):

    def __init__(self, events):
        self.events = events
        
    def execute_order(self, event):
        if event.type == 'ORDER':
            fill_event = FillEvent(event.stamp,
                            event.symbol, 'BROKER', event.quantity,
                            event.order_type)
            self.events.put(fill_event)
```
Pretty straight forward, the Broker initializes our Event Queue, to "put" events in, as its only required argument. It contains the abstract method required to take in specific OrderEvent and fulfill it, thus creating a FillEvent and put it in the queue.

### 4. DATA.PY
Now we will start on one of our essential components. [COMING SOON]
