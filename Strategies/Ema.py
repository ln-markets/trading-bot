from math import floor
from time import sleep, time

from lnmarkets import rest
from Lnmclient import Lnmclient

import json
import datetime as dt
import logging


class Ema():


# Connection to LNMarkets API
    def __init__(self, options):
        lnm = rest.LNMarketsRest(**options)
        lnm.futures_get_ticker()
        self.lnm = lnm
        self.client = Lnmclient(options)


# Compute a SMA to initialize EMA
    def firsts_ema(self, time, nb_periods, big_periods, time_scale):
        t_ref = dt.datetime.fromtimestamp(time)
        if time_scale == 'minutes':
            delta = dt.timedelta(minutes=nb_periods+big_periods+1)
        else:
            delta = dt.timedelta(hours=nb_periods+big_periods+1)
        t_ini = t_ref - delta
        sma = 0
        counter = 0
        for k in range(0, nb_periods, nb_periods//10):
            minutes = dt.timedelta(minutes=k)
            hours = dt.timedelta(hours=k)
            if time_scale == 'minutes':
                timestamp_mili = round(1000 * dt.datetime.timestamp(t_ini + minutes))
            else:
                timestamp_mili = round(1000 * dt.datetime.timestamp(t_ini + hours))
            sleep(2)
            sma += json.loads(self.lnm.futures_index_history({"to": timestamp_mili, "limit": 1}))[0]["index"]
            counter += 1
        sma /= counter
        return [sma]


# Compute the new EMA
    def compute_ema(self, price, previous_ema, nb_periods):
        constant = 2 / (nb_periods + 1)
        new_ema = (price - previous_ema) * constant + previous_ema
        return new_ema


## Ema bot uses 2 EMAs (Exponential Moving Average) with two differents range period and open a position when they cross.
# Only one position is opened
# Inputs are detailed in Configuration file
# Output is the position taken by the bot
    def ema_bot(self, quantity = 20, leverage = 10, little_period = 50, big_period = 200, time_scale = 'minutes'):
        # Other parameters you can adjust. Be carful, if stoploss or takeprofit is not in the good range, your positions will not be opened.
        stoploss_long = None
        stoploss_short = None
        takeprofit_long = None
        takeprofit_short = None
        logging.basicConfig(level=logging.INFO) # for which type of message you want to be notified

        emas_little = []
        emas_big = []
        upper = 'middle'
        time_remaining = big_period

        while True:
            # computation of EMAs first values. It's necessary to be accurate
            while time_remaining > 0:
                if emas_little == []:
                    logging.info(dt.datetime.fromtimestamp(time()))
                    logging.info(' Initialization in progress')
                    t = time()
                    #SMAs
                    emas_little = self.firsts_ema(t, little_period, big_period, time_scale)
                    emas_big = self.firsts_ema(t, big_period, big_period, time_scale) 
                else:
                    # new EMAs
                    t_ref = dt.datetime.fromtimestamp(time())
                    if time_scale == 'minutes':
                        delta = dt.timedelta(minutes=time_remaining)
                    else:
                        delta = dt.datetime(hours=time_remaining)
                    t = t_ref - delta
                    timestamp_mili = round(1000 * dt.datetime.timestamp(t))
                    sleep(2)
                    price = json.loads(self.lnm.futures_index_history({"to": timestamp_mili, "limit": 1}))[0]
                    price = price["index"]
                    previous_ema_little = emas_little[-1]
                    previous_ema_big = emas_big[-1]
                    ema_little = self.compute_ema(price, previous_ema_little, little_period)
                    emas_little.append(ema_little)
                    ema_big = self.compute_ema(price, previous_ema_big, big_period)
                    emas_big.append(ema_big)
                    time_remaining -=1
            if upper == 'middle':
                logging.info(dt.datetime.fromtimestamp(time()))
                logging.info(' Initialization done. Waiting for a cross')

            # new EMAs
            price = json.loads(self.lnm.futures_index_history({"to": round(1000*time()), "limit": 1}))[0]["index"]
            previous_ema_little = emas_little[-1]
            previous_ema_big = emas_big[-1]
            ema_little = self.compute_ema(price, previous_ema_little, little_period)
            emas_little.append(ema_little)
            ema_big = self.compute_ema(price, previous_ema_big, big_period)
            emas_big.append(ema_big)

            # upper represents the upper curve of the graph
            if ema_little >= ema_big:
                new_upper = 'little'
            else:
                new_upper = 'big'
            # check if there is a cross
            if new_upper == 'little' and upper == 'big':
                quantity = min(quantity, floor(json.loads(self.lnm.get_user())["balance"]*price*leverage*10**(-8)))
                # display the cross
                logging.info(dt.datetime.fromtimestamp(time()))
                logging.info(' Golden cross ! It is time to buy')
                # return the position opened
                return self.client.buy_market(leverage, quantity, None, stoploss_long, takeprofit_long)
            elif new_upper == 'big' and upper == 'little':
                quantity = min(quantity, floor(json.loads(self.lnm.get_user())["balance"]*price*leverage*10**(-8)))
                logging.info(dt.datetime.fromtimestamp(time()))
                logging.info(' Death cross ! It is time to sell')
                return self.client.sell_market(leverage, quantity, None, stoploss_short, takeprofit_short)
            # update upper
            upper = new_upper
            # wait before computing new EMAs
            if time_scale == 'minutes':
                sleep(60)
            else:
                sleep(3600)


# Simulate a ema-based strategy in the past
# Only one position is opened
# Output is the P&L of this strategy
    def backtest(self, initial_datetime, quantity = 20, leverage = 10, little_period = 50, big_period = 200, time_scale = 'hours'):
        initial_timestamp = dt.datetime.timestamp(dt.datetime.fromisoformat(initial_datetime))

        # Other parameters you can adjust. Be carful, if stoploss or takeprofit is not in the good range, your positions will not be opened.
        stoploss_long = None
        stoploss_short = None
        takeprofit_long = None
        takeprofit_short = None
        evaluate = True # compute the p&l you would have
        time_before_eval = 600 # your p&l will be computed this number of minutes after position's opening
        logging.basicConfig(level=logging.INFO) # for which type of message you want to be notified

        emas_little = []
        emas_big = []
        upper = 'middle'
        time_remaining = big_period
        counter = 0
        if time_scale == 'minutes':
            multiplier = 60
        else:
            multiplier = 3600

        while True:
            while time_remaining > 0:
                if emas_little == []:
                    t = initial_timestamp
                    emas_little = self.firsts_ema(t, little_period, big_period, time_scale)
                    emas_big = self.firsts_ema(t, big_period, big_period, time_scale) 
                else:
                    t_ref = dt.datetime.fromtimestamp(initial_timestamp)
                    if time_scale == 'minutes':
                        delta = dt.timedelta(minutes=time_remaining)
                    else:
                        delta = dt.timedelta(hours=time_remaining)
                    t = t_ref - delta
                    timestamp_mili = round(1000 * dt.datetime.timestamp(t))
                    sleep(2)
                    price = json.loads(self.lnm.futures_index_history({"to": timestamp_mili, "limit": 1}))[0]["index"]
                    previous_ema_little = emas_little[-1]
                    previous_ema_big = emas_big[-1]
                    ema_little = self.compute_ema(price, previous_ema_little, little_period)
                    emas_little.append(ema_little)
                    ema_big = self.compute_ema(price, previous_ema_big, big_period)
                    emas_big.append(ema_big)
                    time_remaining -=1

            sleep(2)
            price = json.loads(self.lnm.futures_index_history({"to": round(1000*(initial_timestamp+multiplier*counter)), "limit": 1}))[0]["index"]
            previous_ema_little = emas_little[-1]
            previous_ema_big = emas_big[-1]
            ema_little = self.compute_ema(price, previous_ema_little, little_period)
            emas_little.append(ema_little)
            ema_big = self.compute_ema(price, previous_ema_big, big_period)
            emas_big.append(ema_big)

            if ema_little >= ema_big:
                new_upper = 'little'
            else:
                new_upper = 'big'
            if new_upper == 'little' and upper == 'big':
                bid = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(initial_timestamp+multiplier*counter)), "limit": 1}))[0]["bid"]
                params = {
                    "type": "m",
                    "side": "b",
                    "leverage": leverage,
                    "quantity": quantity,
                    "margin": round(10**8*quantity/(bid*leverage)),
                    "time": round(initial_timestamp+multiplier*counter),
                    "stoploss": stoploss_long,
                    "takeprofit": takeprofit_long,
                    "entry_price": bid,
                    "index_price": price,
                    "currently": "running",
                    "pl": None,
                }
                logging.info(' Golden cross detected at ' + str(dt.datetime.fromtimestamp(initial_timestamp+3600*counter)))
                # position not really opened but stored in a json file
                self.client.store_json('Backtest.json', params)
                if evaluate:
                    return self.client.evaluate_backtest('Backtest.json', params["time"]+time_before_eval*60)
                return ' New position opened. You can consult it in Backtest.json file'
            elif new_upper == 'big' and upper == 'little':
                # collect previous data in LNM price history database
                offer = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(initial_timestamp+multiplier*counter)), "limit": 1}))[0]["offer"]
                params = {
                    "type": "m",
                    "side": "s",
                    "leverage": leverage,
                    "quantity": quantity,
                    "margin": round(10**8*quantity/(offer*leverage)),
                    "time": round(initial_timestamp+multiplier*counter),
                    "stoploss": stoploss_short,
                    "takeprofit": takeprofit_short,
                    "entry_price": offer,
                    "index_price": price,
                    "currently": "running",
                    "pl": None,
                }
                logging.info(' Death cross detected at ' + str(dt.datetime.fromtimestamp(initial_timestamp+multiplier*counter)))
                self.client.store_json('Backtest.json', params)
                if evaluate:
                    # evaluate the profit and loss of each position stored in json file
                    return self.client.evaluate_backtest('Backtest.json', params["time"]+time_before_eval*60)
                return ' New position opened. You can consult it in Backtest.json file'
            upper = new_upper
            counter += 1
    
