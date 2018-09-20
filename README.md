
# Algorithmic Trading Program


## Table of Contents
 - [Introduction](https://github.com/xphysics/AlgorithmicTrading#introduction)
 - [Features Log](https://github.com/xphysics/AlgorithmicTrading#features-log)
 - [General Blueprint](https://github.com/xphysics/AlgorithmicTrading#blueprint)
 - [Components Breakdown/How-To-Use](https://github.com/xphysics/AlgorithmicTrading#components-breakdownhow-to-use)
   - [backtest.py](https://github.com/xphysics/AlgorithmicTrading#1-backtestpy---run-to-start-backtesting-process)
   - [event.py](https://github.com/xphysics/AlgorithmicTrading#2-eventpy)
   - [broker.py](https://github.com/xphysics/AlgorithmicTrading#3-brokerpy)
   - [data.py](https://github.com/xphysics/AlgorithmicTrading#4-datapy)

## Introduction
Algorithmic trading allows individuals to rid fundamental and psychological hunches, or guessings, when trading any financial markets, stocks, bonds, forex, options, etc. With the extensive and flexible event-driven structure of this project, users can craft customary component templates, such as portfolio, dataframe or algo strategies, and implement them to backtest on any desired market, as long as time series data is available. This program is an ongoing and continuously improving database, with potentially endless implementations to be added.

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

The goal of trading financial markets quantitatively is to continuously perform necessary calculations and adjustments in position sizings, allocations, market predictions and risk management through market analysis, etc. This implies the majority of quantitative decision making and calculations reside within Strategy & Portfolio components. Future live testing implementations will require major updates on the Broker component.

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
                    self.commission = self.calculate_commission()
                else:
                    self.commission = commission

    def calculate_commission(self):
    # OPTIONAL FOR NOW: OUR CURRENT MODEL JUST ASSUME NO COMMISSION REQUIRED FOR SIMPLICITY
            return 0
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

#### 4. DATA.PY
Now we will start on one of our essential components. DataFrame is responsible for handling and showing data for other components to access for usage, like retreiving latest bars, timestamps, etc.
Again, after importing necessary modules, we will create a general DataFrame class with defined abstract methods to be included in templates.
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
    
    @abstractmethod
    # [OPTIONAL] use to add any additional data to the dataframe base on calculations off market OHLCV data
    def add_data(self,symbols,periods,sma,ewma,
                arith_ret,hpfilter,log_ret,d1close,d2close):
        raise NotImplementedError('implement add_sma() to proceed') 

```
Now that we're done with setting up a general DataFrame class for our template to inherit on. We will proceed on creating the actual dataframe that will be used, we'll name it CSVData.
Let's first tell what our DataFrame to initialize when being called with given arguments: events, csv_path, and symbols. All of which were already defined above.
```python
class CSVData(DataFrame):
    def __init__(self, events, csv_path, symbols):
        self.events = events
        self.csv_path = csv_path
        self.symbols = symbols
        self.symbol_data = {} # all csv data
        self.timestamp = None # timestamp will be set after load.csv() is run
        self.latest_stamps = [] # use to track our timeindex
        self.latest_symbol_data = {} # latest data updated by update_bars()
        self.continue_backtest = True
        # After initializing all variables, we load all symbols' csv files (OHLCV) into symbol_data as generators
		# We'll go over load_csv() next
        self.load_csv()
```
The last line of our initialization process is load_csv(), a function which we will go over next. This function basically is completely responsible for uploading historical financial data on desired symbols (stocks) from the csv_path defined. Meaning that regardless of whether we have data for it or not, our DataFrame will automatically download desired data using Alpha Vantage free API, which is included in the repositories.

First we'll perform check to whether the csv data exists or not,. This is an interactive process and the only one we need as it will be prompted the moment backtest.py runs. If there's no csv data available for certain symbols, it will print them out. Finally, it will ask the user if he, or she, want to perform Check and Update, which we will go over next.

```python
    def load_csv(self):
        indexes = None
		columns = ['open','high','low','close','volume']
        not_seen = []
        for i in self.symbols:
            path_check = os.path.exists(self.csv_path+'/'+i+'.csv')
            if path_check == True:
                pass
            elif path_check == False:
                not_seen.append(i)
        if len(not_seen) == 0:
            print('Data available for all symbols')
        else:
            print('Database is missing data for the following symbol(s): ')
            for i in not_seen:
                print(i)
            print('Backtest cannot start with missing data')
            print('Y = perform update process (might take a minute or two)')
            print('N = drop missing symbol data(s) and proceed')
        if len(not_seen) == 0:
            db_check = input('Wanna check and update database for potential new data? (Y/N): ')
        else:
            db_check = input('Wanna check and update database,? (Y/N): ')
        if str(db_check).lower() == 'y':
            self.check_and_update(symbols=self.symbols) # this is another functions we will go over next
        else:
            print('Dataframe launched with pre-existing data')
```
After we check data availability and perform check_and_update if prompted (we will go over it next), we will go ahead and load up our csv data to the dataframe.
```python
		for i in self.symbols:
			self.symbol_data[i] = pd.read_csv(os.path.join(self.csv_path,
											'{file_name}.{file_extension}'.format(file_name=i,
                                        	file_extension='csv')),
                                        	header = 0, index_col = 0)
											
			self.symbol_data[i].columns = columns # clean up columns by re-assigning it 
			self.symbol_data[i] = self.symbol_data[i].sort_index() #sort index to make sure it's monotonic
            if indexes is None:
				indexes = self.symbol_data[i].index
            else:
                indexes.union(self.symbol_data[i].index)
            self.latest_symbol_data[i] = [] #set latest symbol data in to a list to be appended later
        self.timestamp = indexes
        for i in self.symbols:
            self.symbol_data[i] = self.symbol_data[i].reindex(index=indexes,method='pad')
```
Now that we've gone over the load_csv(), an essential thing we will go over within it is our exclusive function check_and_update. I included an API key in there for usage but if you're gonna use it for yourself consistently, get your own API key. 
DataFrame's check_and_update will basically get your data ready and as up-to-date, pulling financial data using Alpha Vantage API.
```python
    def check_and_update(self,symbols, interval = '1min'):
        api_keys = ['0GSGYX7YU9H0UHHZ','7ZL6EROSN2W13QP3'] #I have 2 api keys to switch if limit reached
        api = 0 #this represents the index of the current api key used	
        for i in symbols:
            check = os.path.exists(self.csv_path+'/'+i+'.csv')
            if check == True: #if data file exists
	    	# Load up existing data in our csv path
	    	csv_data = pd.read_csv(os.path.join(self.csv_path,
					'{file_name}.{file_extension}'.format(file_name = i,
					file_extension = 'csv')),header = 0, index_col = 0)
                if (((datetime.date.today().day) > (datetime.datetime.strptime(csv_data.index[-1],'%Y-%m-%d %H:%M:%S').day)) or ((datetime.date.today().month) > (datetime.datetime.strptime(csv_data.index[-1], '%Y-%m-%d %H:%M:%S').month))) and (datetime.date.today().weekday() < 5):
					# if today's day or month is later/more than csv's latest day or month (respectively)
                    # AND that today isn't Saturday or Sunday
                    # we will download new data and update
                    new = None
                    print(i+ '\'s ' + 'OHLCV data is outdated. Updating...')
                    while type(new) != pd.DataFrame:
                        try:
                            ts = TimeSeries(key=api_keys[api], output_format = 'pandas') #imported method from alpha_vantage
                            new = ts.get_intraday(symbol = i, interval = interval, outputsize = 'full')[0]
                        except ValueError:
                            print('API Call at Limit for ' + i+ '\'s OHLCV data...switching to another API key, and sleep for 5 seconds..')
                            if api == 0:
                                api = 1
                            elif api == 1:
                                api = 0
                            time.sleep(5)
			    
		    		# reset new data by dropping existing ones if there are any
                    new = new.drop(new.index.intersection(csv_data.index))
					
		    		# add new data to existing csv data, right beneath it, since we already dropped intersecting indexes
                    csv_data = csv_data.append(new)
					
		    		# save the newly updated data
                    csv_data.to_csv(os.path.join(self.csv_path,
                            '{file_name}.{file_extension}'.format(file_name = i,
                            file_extension = 'csv')))
                else:
                    print(i+ '\'s ' + 'OHLCV data is up to date. No update needed.')
                    # other, aka latest csv's latest timestamp is up to date, we won't do anything
                    pass
            elif check == False: # if no data file exists
	    	# this is basically the same as above
                print(i+ '\'s ' + 'OHLCV data not found in database. Downloading and saving latest data...')
                new = None
                while type(new) != pd.DataFrame:
                    try:
                        ts = TimeSeries(key=api_keys[api], output_format = 'pandas')
                        new = ts.get_intraday(symbol = i, interval = interval, outputsize = 'full')[0]
                    except ValueError:
                        print('API Call at Limit for ' + i+ '\'s OHLCV data...switching to another API key, and sleep for 5 seconds..')
                        if api == 0:
                            api = 1
                        elif api == 1:
                            api = 0
                        time.sleep(5)
                new.to_csv(os.path.join(self.csv_path,
                            '{file_name}.{file_extension}'.format(file_name = i,
                            file_extension = 'csv')))
```
Now that we're done with initilization, we will over the ABSTRACT METHODS that our general DataFrame class established. These are fairly straight forward as it's responsible for interactions between different components to handle data.
First, we have to understand how data is being handled in our event-driven system. During our initlization proess. We have initialized several important variables: 
 - `timestamp`: All csv timestamps established when load_csv() was called
 - `latest_stamps`: Stamps of bars that have been updated onto the dataframe
 - `symbol_data`: All csv data established during load_csv()
 - `latest_symbol_data`: bars that have been updated onto the dataframe
As you can see, for timestamps and bars, we are keeping track of them with two different variables, one for tracking all updated bars+stamps and one contains all bars+stamps that loaded by load_csv()
Now that we understand how this works, we will write our abstract functions.
```python
	# This is used by abstract method update_bars() to obtain the new bar
    def get_new_bar(self,symbol,stamp):
        csv_data = self.symbol_data[symbol]
        new_bar = csv_data.loc[stamp] #bar contains informations, with its name = stamp
        return new_bar #return a pandas series to be appended to latest_symbol_data
	
	def update_bars(self,stop_at=None):
        # before updating bars, we need to grab the next timestamp and delete it from our existing ones
        try:
			# stamps are in monotonically increasing order, we will grab the first index as the next bar
            stamp = self.timestamp[0]
			
			# append the stamp to latest_stamps
            self.latest_stamps.append(stamp)
			
			# drop if from our timestamp track
            self.timestamp = self.timestamp.drop(stamp)
			
			# Now that have the stamp, we will use get_new_bar to grab the bar correspond to the stamp
            for i in self.symbols:
                bar = self.get_new_bar(i,stamp)
                if bar is not None:
					# append new bar to latest_symbol_data
                    self.latest_symbol_data[i].append(bar)
			
			# IMPORTANT: THIS WILL THEN PLACE A MARKETEVENT WITH THE NEWEST STAMP IN QUEUE
            self.events.put(MarketEvent(stamp))
			# [optional: enter date in string format as csv indexes to tell backtest to stop at certain time]
            if stop_at == None:
                pass
            else:
                if stamp == stop_at:
                    self.continue_backtest = False
                    print('As instructed, backtest stops at:',str(stop_at))
		# We perform our update_bars() with try and except to identify when there's no more stamps to be obtained
		# This means that our timestamps is empty, thus will cause an IndexError problem
		# leading no more data is available to load, thus backtest will be terminated.
        except IndexError:
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
            elif N < 0:
                print('N needs to be an integer >= 0')
            elif N > 0:
                return bars_list[-N:]
	
	# [OPTIONAL]
	def add_data(self,symbols,periods=None,sma=False,ewma=False,
                arith_ret=False,hpfilter=False,log_ret=False,d1close=False,d2close=False):
        # use to add any additional calculations for backtesting data during initlization
        # all calculations are performed on close price, usually called by Strategy's initialization
        # default None assigned to minimize errors
        print('--------------------------------------------------------')
        print('----------ADDING REQUESTED DATA FROM STRATEGY-----------')
        print('--------------------------------------------------------')
        if sma == True:
            print('-> Simple Moving Average (SMA) with periods',str(periods))
        if ewma == True:
            print('-> Exponentially Weighted Moving Average (EWMA) with periods',str(periods))
        if arith_ret == True:
            print('-> Arithmetic Daily Returns')
        if hpfilter == True:
			# This is not recommended for tick by tick calculations since it's a static trend filter
            print('-> HP (Hodrick-Prescott) Filter')
        if log_ret == True:
            print('-> Logarithmic Daily Returns (log of Arithmetic)')
		if d1close == True:
			print('-> First-Order Difference (on Close)')
		if d2close == True:
			print('-> Second-Order Difference (on Close)')
        else:
            print('--> NONE')
        print('--------------------------------------------------------')
        if (type(periods) == list) and ((sma == True) or (ewma == True)):
            index_to_drop = max(periods)-1 #dropping indexes that contain NaN, which resulted from periodic calculations
        elif (arith_ret == True) or (log_ret == True):
            index_to_drop = 1
        else:
            index_to_drop = 0
        self.timestamp = self.timestamp.drop(self.timestamp[:index_to_drop])
        for i in symbols:
            if sma == True:
                for p in periods:
                    self.symbol_data[i]['sma'+str(p)] = self.symbol_data[i]['close'].rolling(p).mean()
            if ewma == True:
                for p in periods:
                    self.symbol_data[i]['ewma'+str(p)] = self.symbol_data[i]['close'].ewm(span=p).mean()
            if arith_ret == True:
                self.symbol_data[i]['arith_ret'] = (self.symbol_data[i]['close']/self.symbol_data[i]['close'].shift(1)) - 1
            if hpfilter == True:
                hpfilter = sm.tsa.filters.hpfilter(self.symbol_data[i]['close'])
                self.symbol_data[i]['hptrend'] = hpfilter[1]
                self.symbol_data[i]['hpnoise'] = hpfilter[0]
            if log_ret == True:
                self.symbol_data[i]['log_ret'] = np.log(self.symbol_data[i]['close']/self.symbol_data[i]['close'].shift(1))
            if d1close == True:
                self.symbol_data[i]['d1close'] = self.symbol_data[i]['close'] - self.symbol_data[i]['close'].shift(1)
            if d2close == True:
                self.symbol_data[i]['d2close'] = self.symbol_data[i]['close'] - self.symbol_data[i]['close'].shift(1)
            self.symbol_data[i] = self.symbol_data[i].drop(self.symbol_data[i].index[:index_to_drop])
```
[MORE COMING SOON]
