# Algorithmic Trading 
### Contributors: Jack, Moritz, Ajay, Lauren
# Abstract
<p>Yet unamed, we are trying to develop a program that allows people to backtest trading strategies on various financial markets. Our data is meant to able to obtain financial data that's desired and apply the algorithms selected to backtest strategies on.</p>
<p> As of now, our program can pull financial data based on the user's parameters, which then it will download and store those data into the directory for the upcoming usage. Below are the supported markets and instructions on how to use the program:</p>
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
<p>As for now. The program can pull financial data on stocks and forex markets, using two different sources: Alpha Vantage & OANDA. We can't use Alpha Vantage api for forex for backtesting purposes since they only provide instantaneous data whenever it's being called. Meawhile OANDA provides forex data for any specified time with any specified interval.</p>
<p>Simply click on below to register for your FREE API keys:</p>
<ul>
	<li><a href="http://bit.ly/2DXVpKM">Alpha Vantage</a></li>
	<li><a href="http://bit.ly/2E7srZP">OANDA</a></li>
</ul>

# Conclusion
N/A
