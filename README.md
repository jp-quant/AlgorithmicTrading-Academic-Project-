# Algorithmic Trading 
### Contributors: Jack, Moritz, Ajay, Lauren
# Abstract
<p>Yet unamed, we are trying to develop a program that allows people to backtest trading strategies on various financial markets. Our program is meant to obtain desired financial data and apply the algorithms selected to backtest strategies on.</p>
<p> As of now, our program can pull financial data based on the user's parameters, which it will then download and store those data into the directory for the upcoming usage. Below are the supported markets and instructions on how to use the program:</p>
<ul>
	<li>Foreign Exchange Currency (Forex)</li>
	<li>Stocks</li>
</ul>

# Instructions

| Parameter            | Type|                Description                           |
|:--------------------:|:---:|:----------------------------------------------------:|
| api                | str | Enter your API Key, depends on what market you're trying to backtest on. OANDA = Forex, Alpha Vantage = Stocks                              |
| market             | str | 'stocks' or 'forex'                             |
| opy_start         | str | Only for Forex usage. Enter your start date in the form of yyyy-mm-dd                            |
| opy_end         | str | Only for Forex usage. Enter your end date in the form of yyyy-mm-dd                             |
| symbols           | list of str | Enter your symbol(s) for the market, ex: 'AAPL', 'EUR_USD'                              |
| interval           | list of str | Enter the interval(s) of your datapoints. For stocks, enter'5min', '15min' etc (read Apha Vantage instructions. For Forex, enter 'M15','H4','D', etc (read OANDA instructions)                             |

# Weekly Progress Log
<h3 style="font-style: italic;">Week 1</h3>
<p>Successfully established an initial framework of the program. We created a base class that's able to pass customizable parameters for the program to execute. This allows any user to use our program on their various purposes.</p>
<p>As of now, the program can pull financial data on stocks and forex markets using two different sources: Alpha Vantage & OANDA. We can't use Alpha Vantage api for forex for backtesting purposes since they only provide instantaneous data whenever it's being called. Meawhile OANDA provides forex data for any specified time with any specified interval.</p>
<p>Simply click on below to register for your FREE API keys:</p>
<ul>
	<li><a href="http://bit.ly/2DXVpKM">Alpha Vantage</a></li>
	<li><a href="http://bit.ly/2E7srZP">OANDA</a></li>
</ul>

<h3 style="font-style: italic;">Week 2</h3>
<p>This week, we collected basic technical indicator data for the program. We began work on creating areas for user input in which users could enter a time interval to show them information about a specific stock or forex currency. We also created error codes.</p>
<p>By the next week, we hope to fix onandapy so that it can pull forex data for Python 2.7 as well as Python 3.6. As of now, users can run the program and input a specific time interval for a specific stock or currency and retrieve a csv file that shows them information on that stock or currency for the time interval entered.</p>
<h3 style="font-style: italic;">Week 3</h3>
<p>This week, we were able to troubleshoot and make oandapy work on Python 3.6. Also, we created a data frame which stores data pulled from the program.</p>
<p> For the future, we hope to write functions for buying, selling, and backtesting. We also hope to add more complex technical indicator data to the program.</p>


# Conclusion
N/A
