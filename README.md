# LN Markets Technical Analysis Bot

A simple bot for algorithmic trading with [Trading View Technical Analysis](https://www.tradingview.com/symbols/XBTUSD/technicals/) signals on [LN Markets](https://lnmarkets.com/).

> :warning: CAUTION: Use at your own risk. This repo is meant to be a reference and has been created for educational purposes only. 

Please use carefully, preferably on Testnet or with small amounts.

## Install

Download this Github repopsitory and install dependencies.
```
pip install -r requirements.txt
```

## Authentication

> For authentication, you need your [LN Markets API](https://docs.lnmarkets.com/api/v1/) **Key**, **Secret**, and **Passphrase**.

Without them, you will not be able to authenticate.

> :warning: **Never share your API Key, Secret or Passphrase**

Open the 'configuration.yml' file and complete with your LN Markets API credentials.
You can also add the paramter network with 'testnet' for [LN Markets Testnet](https://testnet.lnmarkets.com/) and 'mainnet' for [LN Markets mainnet](https://lnmarkets.com/).

## Strategies

Current available strategies are:
- ta_summary: use the [Trading View Technical Analysis](https://www.tradingview.com/symbols/XBTUSD/technicals/) summary indicator based on 27 signals (oscillators and moving averages) to open and keep a long or short future position
- More to come
More details below.

Open the 'configuration.yml' file.
Then choose the strategy you want for your trading bot affecting True to the corresponding variable (and False to others).
```
# Example
Strategies: 
  ta_summary: True
```

## Parameters

In 'configuration.yml', you can define some parameters to customize your strategy.

```
# Example
ta_summary:
  quantity: 10 #type=int, min=1, quantity of each open position
  leverage: 10 #type=int, min=1, max=100
  interval: '5m' #type=string, available interval between 2 TA summary signals: "1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1W", "1M"
  timeout: 60 #type=int, min=1, number of minutes the trading strat will be running  
```

## Run program

Open 'main.py' file and simply run it. If there is no error, you should see this message in the terminal:
```
Connection to LN Markets ok!
```
If not, double check the API Key, Secret, and Passphrase you  entered.

[LN Markets API](https://docs.lnmarkets.com/api/v1/) has requests limits (30 requests per minute).

## ta_summary

How does it work?  
Once the bot is launched, it follows [Trading View Technical Analysis](https://www.tradingview.com/symbols/XBTUSD/technicals/) summary indicator based on 27 signals (oscillators and moving averages) to open and keep running a long Future position while the signal is "BUY" or "STRONG BUY", open and keep running a short Future position while the signal is "SHORT" or "STRONG SHORT", or close any position while the signal is "NEUTRAL".
While the bot is running, you can have either 0 or 1 position running maximum. 

### Parameters to customize the bot
- quantity: the quantity (in USD) for the position running
- leverage: the leverage for the position running
- interval: interval between 2 TA summary signals: "1m" for 1 minute, "5m" for 5 minutes, "15m" for 15 minutes, "30m" for 30 minutes, "1h" for 1 hour, "2h" for 2 hours, "4h" for 4 hours, "1d" for 1 day, "1W" for 1 week, "1M" for 1 month
- interval: number of minutes the trading strat will be running

```
# Example
ta_summary:
  quantity: 10 #type=int, min=1, quantity of each open position
  leverage: 10 #type=int, min=1, max=100
  interval: '5m' #type=string, available interval between 2 TA summary signals: "1m", "5m", "15m", "30m", "1h", "2h", "4h", "1d", "1W", "1M"
  timeout: 60 #type=int, min=1, number of minutes the trading strat will be running
```

## History of trades

After timeout, you will find all the bot's trades during its execution in the CSV 'df_closed_pos.csv' in the folder Strategies.

## To go further

Feel free to customize the bot and add your own strategies.

If you want to use more features from [LN Markets API](https://docs.lnmarkets.com/api/v1/), checkk out the full documentation.