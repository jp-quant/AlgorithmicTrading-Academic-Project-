# Algorithmic Trading Engine
# Introduction
<p> Algo trading allows individuals to rid fundamental and psychological hunches, or guessings, when trading any financial markets. With an extensive and flexible structure, users can craft new essential components, such as portfolio, dataframe or event strategies/algorithms, and implement them to backtest on any desired market, as long as time series data is available. </p>
<p> This program is an ongoing and continuously improving database, with potentially endless implementations to be added.</p>

# Event-Driven Blueprint
<p> Our engine is structured to be an event-driven system. Although slower than vectorised backtesting structure, by doing this, in addition to ridding psychological hunches and guessing, written codes can be recycled to adapt to live trading in the future. </p>
<p> Components are listed sequentially below, ascending from most basic to complex. As each component inherits the ones above, the last component, Strategy, is where most quantitative work reside.</p>
<ul>

<li><strong>Event:</strong> This is the simplest yet key component in our engine. Due to the nature of event-driven structure, we require a fundamental class that could identify what action to proceed taking in an event loop. There are different event types, noted in event.py: MarketEvent, SignalEvent, OrderEvent, FillEvent</li>
</ul>
<ul>
<li><strong>Broker:</strong> A broker is essential to perform any trade. At the moment, we are focusing on developing a solid backtesting engine before moving on to livetrading. Therefore, our current Broker component is extremely simple as it is purely responsible for fulfilling order requested by our Portfolio component. It will then place a </li>
</ul>
<ul>
<li><strong>DataFrame:</strong> First of important components, we need a dataframe that contains all data for portfolio and strategy to use. At the moment, our CSVHistoricalDataFrame is the only one existed as its being tailored to adapt to Strategy and Portfolio's backtesting needs, such as adding additional calculated data on top of market OHCLV data, logging backtesting progresses, or data categorizations.</li>
</ul>
<ul>
<li><strong>Portfolio:</strong> It being on the ladder of importance, we need a portfolio management class that handles the order and logic of positions being placed, current and subsequents. Portfolio will keep track of each asset value and positions, along with updating them after orders are executed. Information of portfolio value and assets allocations are essential to optimize our portfolio as much as possible. NOTE: Portfolio optimization can be placed in either Portfolio or Strategy, but preferrably Strategy, as it being the most important component, thus having access to ALL other components, including our Portfolio.</li>
</ul>
<ul>
<li><strong>Strategy:</strong> This is where most high-end quantitative contents reside. Strategy inherits all the classes/components above, as it can observe and capture latest financial data having access to our DataFrame, on top of montoring our portfolio. Calculations performed periodically during trading can all be made in this most valuable component. </li>
</ul>
<p> The goal of trading financial markets quantitatively is to continuously perform necessary calculations and adjustments in position sizings, allocations, market predictions and risk management through market analysis, etc. This imply the majority of quantitative decision making and calculations reside within Strategy & Portfolio components.</p>
