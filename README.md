
# Algorithmic Trading Program

------------

### Introduction
------------
Algorithmic trading allows individuals to rid fundamental and psychological hunches, or guessings, when trading any financial markets, stocks, bonds, forex, options, etc. With the extensive and flexible event-driven structure of this project, users can craft new customary components, such as portfolio, dataframe or algo strategies, and implement them to backtest on any desired market, as long as time series data is available. This program is an ongoing and continuously improving database, with potentially endless implementations to be added.

------------
### Blueprint
------------

Our engine is structured to be an event-driven system. Although slower than vectorised backtesting structure, by doing this, in addition to ridding psychological hunches and guessing, written codes can be recycled to adapt to live trading in the future. Components are listed sequentially below, ascending from most basic to complex. As each component inherits the ones above, the last component, Strategy, is where most quantitative work reside.

1. **EVENT:** This is the simplest yet key component in our engine. Due to the nature of event-driven structure, we require a fundamental class that could identify what action to proceed taking in an event loop. There are different event types, noted in event.py: MarketEvent, SignalEvent, OrderEvent, FillEvent.

3. **BROKER:** A broker is essential to perform any trade. At the moment, we are focusing on developing a solid backtesting engine before moving on to livetrading. Therefore, our current Broker component is extremely simple as it is purely responsible for fulfilling order requested by our Portfolio component. It will then place a FillEvent to notify out Portfolio that the order has been executed so we could update our portfolio. 

5. **DATAFRAME:**  First of important components, we need a dataframe that contains all data for portfolio and strategy to use. At the moment, our CSVHistoricalDataFrame is the only one existed as its being tailored to adapt to Strategy and Portfolio's backtesting needs, such as adding additional calculated data on top of market OHCLV data, logging backtesting progresses, or data categorizations.

7. **PORTFOLIO:** It being on the ladder of importance, we need a portfolio management class that handles the order and logic of positions being placed, current and subsequents. Portfolio will keep track of each asset value and positions, along with updating them after orders are executed. Information of portfolio value and assets allocations are essential to optimize our portfolio as much as possible. NOTE: Portfolio optimization can be placed in either Portfolio or Strategy, but preferrably Strategy, as it being the most important component, thus having access to ALL other components, including our Portfolio.

9. **STRATEGY:** This is where most high-end quantitative contents reside. Strategy inherits all the classes/components above, as it can observe and capture latest financial data having access to our DataFrame, on top of montoring our portfolio. Calculations performed periodically during trading can all be made in this most valuable component. 

The goal of trading financial markets quantitatively is to continuously perform necessary calculations and adjustments in position sizings, allocations, market predictions and risk management through market analysis, etc. This imply the majority of quantitative decision making and calculations reside within Strategy & Portfolio components. Future live testing implementations will require major updates on the Broker component.

------------
###  Getting Started/ How-To-Use
------------
-  ** REQUIREMENTS**
- If you do not have Python 3.7, download it [here](https://www.python.org/downloads/release/python-370/ "here").
- In terminal, navigate to project directory and type `pip install -r requirements.txt` to install all required modules for usage.
------------

1. ** backtest.py ** - (*Run to start backtesting process*)
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
[MORE INSTRUCTIONS COMING SOON]
