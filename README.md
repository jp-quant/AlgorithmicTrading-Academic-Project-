
# Algorithmic Trading Program
First Sample Strategy (2/9/19): Portfolio Sharpe Maximization

## Table of Contents
 - [Introduction](https://github.com/xphysics/AlgorithmicTrading#introduction)
 - [Features Log](https://github.com/xphysics/AlgorithmicTrading#features-log)
 - [General Blueprint](https://github.com/xphysics/AlgorithmicTrading#blueprint)
 - [Components Breakdown/How-To-Use](https://github.com/xphysics/AlgorithmicTrading#components-breakdownhow-to-use)
   - [OBTAIN DATA & CONSTRUCT DATAFRAME](https://github.com/xphysics/AlgorithmicTrading#1)
   - [backtest.py](https://github.com/xphysics/AlgorithmicTrading#2-backtestpy---run-to-start-backtesting-process)
   - [event.py](https://github.com/xphysics/AlgorithmicTrading#3-eventpy)
   - [broker.py](https://github.com/xphysics/AlgorithmicTrading#4-brokerpy)

## Introduction
Algorithmic trading allows individuals to rid fundamental and psychological hunches, or guessings, when trading any financial markets, stocks, bonds, forex, options, etc. With the extensive and flexible event-driven structure of this project, users can craft customary component templates, such as portfolio, dataframe or algo strategies, and implement them to backtest on any desired market, as long as time series data is available. This program is an ongoing and continuously improving database, with potentially endless implementations to be added.

## Features Log
 - Only focus on backtesting engine first, live trading will be implemented in the future with more updated Broker
 - Stocks data are downloaded and updated using Alpaca API, register [HERE](https://alpaca.markets/ "HERE").
 - First Sample Strategy (2/9/19): Portfolio Sharpe Maximization

## General Blueprint
Our engine is structured to be an event-driven system. Although slower than vectorised backtesting structure, by doing this, in addition to ridding psychological hunches and guessing, written codes can be recycled to adapt to live trading in the future. Components are listed sequentially below, ascending from most basic to complex. As each component inherits the ones above, the last component, Strategy, is where most quantitative work reside.

1. **EVENT:** This is the simplest yet key component in our engine. Due to the nature of event-driven structure, we require a fundamental class that could identify what action to proceed taking in an event loop. There are different event types, noted in event.py: MarketEvent, SignalEvent, OrderEvent, FillEvent.

3. **BROKER:** A broker is essential to perform any trade. At the moment, we are focusing on developing a solid backtesting engine before moving on to livetrading. Therefore, our current Broker component is extremely simple as it is purely responsible for fulfilling order requested by our Portfolio component. It will then place a FillEvent to notify out Portfolio that the order has been executed so we could update our portfolio. 

5. **DATAFRAME:**  First of important components, we need a dataframe that contains all data for portfolio and strategy to use. At the moment, our CSVHistoricalDataFrame is the only one existed as its being tailored to adapt to Strategy and Portfolio's backtesting needs, such as adding additional calculated data on top of market OHCLV data, logging backtesting progresses, or data categorizations.

7. **PORTFOLIO:** It being on the ladder of importance, we need a portfolio management class that handles the order and logic of positions being placed, current and subsequents. Portfolio will keep track of each asset value and positions, along with updating them after orders are executed. Information of portfolio value and assets allocations are essential to optimize our portfolio as much as possible. NOTE: Portfolio optimization can be placed in either Portfolio or Strategy, but preferrably Strategy, as it being the most important component, thus having access to ALL other components, including our Portfolio.

9. **STRATEGY:** This is where most high-end quantitative contents reside. Strategy inherits all the classes/components above, as it can observe and capture latest financial data having access to our DataFrame, on top of montoring our portfolio. Calculations performed periodically during trading can all be made in this most valuable component. 

The goal of trading financial markets quantitatively is to continuously perform necessary calculations and adjustments in position sizings, allocations, market predictions and risk management through market analysis, etc. This implies the majority of quantitative decision making and calculations reside within Strategy & Portfolio components. Future live testing implementations will require major updates on the Broker component.

##  Components Breakdown/How-To-Use
#### Getting Started
- If you do not have Python 3.6.5, download it [here](https://www.python.org/downloads/release/python-365/ "here").
- In terminal, navigate to project directory and type `pip3 install -r requirements.txt` to install all required modules for usage.

------------
#### 1. OBTAIN DATA & CONSTRUCT DATAFRAME [data.py]
To even start our backtesting process, we first need to gather market data to be traded/backtested on.
We will first proceed to build our dataframe for other modules to be used. The dataframe's blueprint is built for future integration of live trading as it is event driven.
Every DataFrame constructed will adhere to the following abstract methods, meaning that it must include these methods for other modules to call upon and use.
```python
class DataFrame(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    # use in other components to obtain latest bars
    def get_latest_bars(self, symbol, N):
        raise NotImplementedError('implement latest_bars() to proceed')

    @abstractmethod
    # use in backtest.py to constantly update bars
    def update_bars(self):
        raise NotImplementedError('implement update_bars() to proceed')

```
Now that we're done with setting up a general DataFrame class for our template to inherit on. We will proceed on creating the actual dataframe that will be used, we'll name it CSVData.
Let's first tell what our DataFrame to initialize when being called with given arguments: events, csv_path, and symbols. All of which were already defined above.
```python
class AlpacaDataFrame(DataFrame):
    def __init__(self, events, csv_path, symbols,interval):
        #-----Initialize params-----#
        self.events = events
        self.csv_path = csv_path +'/'+interval.lower()
        self.symbols = symbols
        self.interval = interval
        #---------------------------#
        self.symbol_data = {}
        self.bars_generator = {}
        self.timestamps = None #timestamp will be set after load.csv() is run
        self.latest_stamps = None #use to track our current time index
        self.latest_symbol_data = {}
        self.continue_backtest = True
        '''
        self.alpaca_api_keys = {'key_id':[YOUR KEY ID],
                                'secret_key':[YOUR SECRET KEY ID]}
        self.alpaca_api = tradeapi.REST(self.alpaca_api_keys['key_id'],self.alpaca_api_keys['secret_key'])
        # After initializing all variables, we load all symbols' csv files (OHLCV) into symbol_data as generators
        self.market_calendar = self.alpaca_api.get_calendar()
        '''
        self.initialize_df(interval=self.interval)
        self.load_warm_up(0.25)
```
One of the last lines of our initialization process is initialize_df(), a function which we will go over next. This function basically is completely responsible for uploading historical financial data on desired symbols (stocks) from the csv_path defined. Meaning that regardless of whether we have data for it or not, our DataFrame will automatically download desired data using Alpaca API (make sure you register for their API, which is free, to be able to use it)

First we'll perform check to whether the csv data exists or not,. This is an interactive process and the only one we need as it will be prompted the moment backtest.py runs. If there's no csv data available for certain symbols, it will print them out. Finally, it will ask the user if he, or she, want to perform update_database(), which we will go over next.

```python
    def initialize_df(self,interval):
        #IMPORTANT: THE ORIGINAL DATA VETTED IN update_database
        #           NEED TO BE FIXED TO ['open','high','low','close','volume']
        indexes = None
        columns = ['open','high','low','close','volume']
        not_seen = []
        for i in self.symbols:
            path_check = os.path.exists(self.csv_path+'/'+i+'.csv') # checking for filled data
            if path_check == True:
                pass
            elif path_check == False:
                not_seen.append(i)

        if len(not_seen) == 0:
            print('Data available for the requested symbol(s)')
            answers = ['y','n']
            db_check = input('Perform update (requires internet) for potential new data? (Y/N): ')
            while str(db_check).lower() not in answers:
                db_check = input('Invalid Input. Please enter \'Y\' for YES and \'Y\' for NO (Y/N): ')

            if str(db_check).lower() == 'y':
                self.update_database(symbols=self.symbols,interval=self.interval)
            elif str(db_check).lower() == 'n':
                pass
        else:
            print('Database is missing data for the following symbol(s): ')
            print('------------------------')
            for i in not_seen:
                print(i)
            print('------------------------')
            print('Commencing Automatic Database Update...')
            self.update_database(symbols = self.symbols,interval=self.interval)
        print('Initializing DataFrame...')
        for i in self.symbols:
            self.symbol_data[i] = pd.read_csv(
                                        os.path.join(self.csv_path,
                                        '{file_name}.{file_extension}'.format(file_name=i,
                                        file_extension='csv')),
                                        header = 0, index_col = 0)
            
            self.symbol_data[i].columns = columns # clean up columns
            self.symbol_data[i] = self.symbol_data[i].sort_index() #sort index to make sure it's monotonic
            # IF WE'RE DATAFRAME INTERVAL IS DAILY, WE'LL JUST GET RID OF TIME FOR THE INDEXES
            if interval[-1] == 'D':
                self.symbol_data[i].index = [d.split(' ')[0] for d in self.symbol_data[i].index]
            if indexes is None:
                indexes = self.symbol_data[i].index
            else:
                indexes.union(self.symbol_data[i].index)
        self.timestamps = indexes
        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index=indexes)
            self.bars_generator[i] = self.symbol_data[i].iterrows()
```
Now that we've gone over the initialize_df(), an essential thing we will go over within it is our exclusive function update_database()
DataFrame's update_database() will basically get your data ready and as up-to-date, pulling financial data using Alpaca API
```python
    def update_database(self,symbols, interval):
        for i in symbols:
            check = os.path.exists(self.csv_path+'/'+i+'.csv')
            if check == True: #if data file exists
                csv_data = pd.read_csv(os.path.join(self.csv_path,
                                                '{file_name}.{file_extension}'.format(file_name = i,
                                                file_extension = 'csv')),header = 0, index_col = 0)
                if (((datetime.date.today().day) > (datetime.datetime.strptime(csv_data.index[-1],'%Y-%m-%d %H:%M:%S').day)) or ((datetime.date.today().month) > (datetime.datetime.strptime(csv_data.index[-1], '%Y-%m-%d %H:%M:%S').month))) and (datetime.date.today().weekday() < 5):
                    # if today's day or month is later/more than csv's latest day or month (respectively)
                    # AND that today isn't Saturday or Sunday
                    # we will download new data and update
                    print(i+ '\'s ' + 'OHLCV data is outdated. Updating...')
                    result = self.get_alpaca_historic(i,interval)
                    result = self.clean_symbol_data(result)
                    result = result.drop(result.index.intersection(csv_data.index)) #resetting result data by dropping existing ones if there are any
                    csv_data = csv_data.append(result)
                    csv_data.to_csv(os.path.join(self.csv_path,
                                '{file_name}.{file_extension}'.format(file_name = i,
                                file_extension = 'csv')))

                else:
                    print(i+ '\'s ' + 'OHLCV data is up to date. No update needed.')
                    pass
            elif check == False: # if no data file exists
                print(i+ '\'s ' + 'OHLCV data not found in database. Downloading and saving latest data...')
                if os.path.exists(self.csv_path):
                    pass
                else:
                    os.makedirs(self.csv_path)
                result = self.get_alpaca_historic(i,interval)
                result = self.clean_symbol_data(result)
                result.to_csv(os.path.join(self.csv_path,
                            '{file_name}.{file_extension}'.format(file_name = i,
                             file_extension = 'csv')))
```
To finish the initialization process, we'll add a function that load a specified percentage amount of bars as warm up bars for initial calculations to place trades
```python
    def load_warm_up(self,percent):
        count = int(percent*len(self.timestamps))
        print('---|LOADING',str(count),'WARM-UP BARS AS',str(percent*100)+'%',' OF AVAILABLE HISTORICAL DATA|---')
        self.latest_stamps = self.timestamps[:count]
        for s in self.symbols:
            self.latest_symbol_data[s] = self.symbol_data[s].loc[self.latest_stamps]
            self.bars_generator[s] = self.symbol_data[s].drop(self.latest_symbol_data[s].index).iterrows()
```
Now that we're done with initilization, we will over the ABSTRACT METHODS that our general DataFrame class established. These are fairly straight forward as it's responsible for interactions between different components to handle data.
First, we have to understand how data is being handled in our event-driven system. During our initlization proess. We have initialized several important variables: 
 - `timestamp`: All csv timestamps established when initialize_df() was called
 - `latest_stamps`: Stamps of bars that have been updated onto the dataframe
 - `symbol_data`: All csv data established during initialize_df()
 - `latest_symbol_data`: bars that have been updated onto the dataframe
As you can see, for timestamps and bars, we are keeping track of them with two different variables, one for tracking all updated bars+stamps and one contains all bars+stamps that loaded by initialize_df()
Now that we understand how this works, we will write our abstract functions.
```python
    def get_new_bar(self,symbol):
        new_bar = next(self.bars_generator[symbol])
        return new_bar[1] #return a pandas series to be appended to latest_symbol_data

    def update_bars(self):
        #before updating bars, we need to grab the next timestamp and delete it from our existing ones
        try:
            for s in self.symbols:
                bar = self.get_new_bar(s)
                if bar.name not in list(self.latest_stamps):
                    self.latest_stamps = self.latest_stamps.append(pd.Index([bar.name]))
                self.latest_symbol_data[s] = self.latest_symbol_data[s].append(bar)
            self.events.put(MarketEvent(self.latest_stamps[-1])) #FIRST START, IMPORTANT
        except StopIteration:
            self.continue_backtest = False
            print('BACKTEST COMPLETE.')
            
    def get_latest_bars(self, symbol, N=1):
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            return 'Symbol is not available from historical data'
        else:
            if N == 0: #N = 0 is set to return ALL bars updated on the dataframe
                return bars_list
            elif N == 1:
                return bars_list.iloc[-N]
            elif N < 0:
                print('N needs to be an integer >= 0')
            elif N > 0:
                return bars_list.iloc[-N:]
```

#### 2. BACKTEST.PY - (Run to start backtesting process)
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
#### 3. EVENT.PY
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
                    self.commission = self.calculate_commission()
                else:
                    self.commission = commission

    def calculate_commission(self):
    # OPTIONAL FOR NOW: OUR CURRENT MODEL JUST ASSUME NO COMMISSION REQUIRED FOR SIMPLICITY
            return 0
```
#### 4. BROKER.PY
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
[MORE COMING SOON]
