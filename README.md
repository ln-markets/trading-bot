# LN Markets Python Bot

A simple bot for algorithmic trading with LN Markets API.

> :warning: CAUTION: Use at your own risk. This repo is meant to be a reference and created for educational purposes only.  Please use carefully, preferably on Testnet or with small amounts.

## Install

Download this Github repopsitory and install dependencies.
```
pip install -r requirements.txt
```

## Authentication

> For authentication, you need your LN Markets API **Key**, **Secret**, and **Passphrase**.

Without them, you will not be able to authenticate.

> :warning: **Never share your API Key, Secret or Passphrase**

Open the 'Configuration.yml' file and complete with your LN Markets API credentials.

Some features using Twitter require a Twitter Developer account. See more below.

## Strategies

Current available strategies are:
- Random: go all-in random or open regular random positions. 
- Twitter: open a position when a pre-selected account tweets about Bitcoin or any other keyword.
- EMA: analyze BTC Exponential Moving Averages and open a position when their values are optimal.  
More details below.
You can also backtest all these strategies.

Open the 'Configuration.yml' file.
Then choose the strategy you want for your trading bot affecting True to the corresponding variable (and False to others).
```
# Example
Strategies: 
  Random: False
  Random_Backtest: False
  Twitter: True
  Twitter_Backtest: False
  Ema: False
  Ema_Backtest: False
```

## Parameters

In 'Credentials.yml', you can define some parameters to customize your strategy.

```
# Example
Twitter:
  fear_and_greed: True
  keywords: ['Bitcoin', 'bitcoin', 'BTC', 'LN', 'Lightning Network', 'LN Markets']
  usernames_long: ['LNMarkets']
  usernames_short: []
  quantity_per_order: 20
  leverage: 10
```

## Run program

Open 'Main.py' file and simply run it. If there is no error, you should see this message in the terminal:
```
Connection to LN Markets done
```
If not, check the API Key, Secret, and Passphrase you have entered.  

LN Markets API has requests limit (30 requests per minute), which explains why initialization or backtests may take some time.

## Random Strategy

How does it work?  
Once the bot is launched, it opens regular positions which are randomly long or short.

### Parameters to custom the bot :
- all_in : allows you to go all in (use all your margin with leverage 100). :warning: Be careful and don't forget the side is random. Enter True to activate this feature.
- max_quantity : quantity (in USD) used by the bot. It will keep opening positions until this quantity is reached or until you stop it.
- max_leverage : for each order, leverage is randomly picked between 1 and max_leverage.
- interval : time in seconds between two positions opening.

```
# Example
Random:
  all_in: False
  max_quantity: 20
  max_leverage: 10
  interval: 600
```

## Twitter Strategy

To perform this strategy, you need a Twitter Developer account. You can create one [here](https://developer.twitter.com/en)  
Then create an app to connect Twitter API.
Save your keys and tokens and copy them in 'Configuration.yml' as twitter credentials.

How does it work?
Select one or several accounts and a list of keywords (like 'Bitcoin') and some twitter accounts. 
Once an account you have preselected tweets one of the keywords, the bot opens a position (long or short depending the account).  
You can also decide your side by following the Fear and Greed Index of the Market. If the market is greedy, the bot will greed too and conversely.  
The bot stops when one of these two events happens so it takes only one position.

### Parameters to custom the bot :
- fear_and_greed: allows you to follow BTC Fear and Greed index on Twitter (@BitcoinFear). Enter True to activate this feature.
- keywords: list of words that trigger an order. Lower caps and upper caps are different.
- usernames_long: list of accounts that trigger a buy.
- usernames_short: list of accounts that trigger a sell.
- quantity_per_order: quantity (in USD) used by the bot.
- leverage

```
# Example
Twitter:
  fear_and_greed: False
  keywords: ['Bitcoin', 'bitcoin', 'BTC', 'LN', 'Lightning Network', 'LN Markets']
  usernames_long: ['LNMarkets']
  usernames_short: ['elonmusk']
  quantity_per_order: 20
  leverage: 10
```

## EMA Strategy

How does it work?  
This strategy is based on EMAs computations. 
What is an EMA (Exponential Moving Average)?
It is a type of moving average (MA) that places a greater weight and significance on the most recent data points. 

Two EMAs are computed: one representing short term price's evolution and the other representing long term evolution.  
Then we can trace a graph with the evolution of theses two indicators during time. 
When the curves are crossing each other, it is a signal (buy if the short term curve becomes up and sell if it becomes down).

> :warning: This strategy is not necessarily reliable. EMAs are computed on a certain time period (for example EMA 50 days). To have more fun and more crosses, this bot computes EMAs on very short periods (minutes or hours). So keep in mind that the signal's strength is less important than usual.

The bot takes only one order and stops after the first cross. The first cross may take some time to happen, especially if you choose to compute one EMA per hour.

### Parameters to custom the bot :
- quantity_per_order: quantity (in USD) used by the bot
- leverage
- little_period: period for the short term EMA
- big_period: period for the long term EMA
- time_scale: scale of little and big periods. Accepted_values are 'minutes' and 'hours'

```
Ema:
  quantity_per_order: 20
  leverage: 10
  little_period: 50
  big_period: 200
  time_scale: 'minutes'
```

## Backtesting

How does it work?  
Backtesting a strategy is testing its P&L in the past. Notice that past performance abolutely does not guarantee future performance.

### Parameters to customize the bot :
- initial datetime: start date of the backtest. Be careful and respect the format. LN Markets data begins in August 2021 so you can't backtest before this date.
- same parameters than classic strategies

```
# Example
Twitter_Backtest:
  initial_datetime: '2022-01-21T16:01'
  fear_and_greed: True
  keywords: ['Bitcoin', 'bitcoin', 'BTC', 'LN', 'Lightning Network', 'LN Markets']
  usernames_long: ['LNMarkets']
  usernames_short: ['elonmusk']
  quantity_per_order: 20
  leverage: 10
```

## To go further

Feel free to customize the bots and modify the code directly:
- in Strategies.Random.random_bot
- in Strategies.Twitter.twitter_bot
- in Strategies.Ema.ema_bot  
At the beginning of these functions, you can modify other parameters for instance to add stoploss and takeprofit or to choose how to evaluate backtested strategies.

If you want to use more features from LN Markets API, check out full documentation [here](https://lnmarkets.com/)
