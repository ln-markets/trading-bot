from random import randint
from math import floor
from time import sleep, time

from lnmarkets import rest
from Lnmclient import Lnmclient

import json
import datetime as dt
import logging


class Random():


# Connection to LNMarkets API
    def __init__(self, options):
        lnm = rest.LNMarketsRest(**options)
        lnm.futures_get_ticker()
        self.lnm = lnm
        self.client = Lnmclient(options)


## Random bot opens a random position every 'interval' seconds until balance is empty or max_quantity is reached.
# Inputs are detailed in Configuration file
# Output can be a graph showing the evolution of your Balance during the strategy
    def random_bot(self, all_in = False, max_quantity = 20, max_leverage = 10, interval = 600):
        # Other parameters you can adjust. Be carful, if stoploss or takeprofit is not in the good range, your positions will not be opened.
        stoploss_long = None
        stoploss_short = None
        takeprofit_long = None
        takeprofit_short = None
        show_graph = True # display a graph which shows your balance evolution during random strategy.
        fixed_quantity = None # if you want the same quantity for each order
        fixed_leverage = None # if you want the same leverage for each order
        logging.basicConfig(level=logging.INFO) # for which type of message you want to be notified

        initial_timestamp = time()
        timestamps = [0]
        user = json.loads(self.lnm.get_user())
        balance = [user["balance"] + user["total_running_margin"] + self.client.get_profit_and_loss()]
        counter = 0
        # random operation to know if the position will be long or short
        long = randint(0,1)

        if all_in:
            logging.info(' You went randomly all in. Savage ! You are a huge degen !')
            if long:
                return self.client.buy_all_in()
            return self.client.sell_all_in()
            
        while True:
            # leverage up to max_leverage
            leverage = randint(1,max_leverage)
            if fixed_leverage != None:
                leverage = fixed_leverage
            price = json.loads(self.lnm.futures_index_history({"limit": 1}))[0]["index"]
            #quantity up to max_quantity or max_balance
            max_order_quantity = min(max_quantity, floor(json.loads(self.lnm.get_user())["balance"]*price*leverage*10**(-8)))
            if max_order_quantity >= 1:
                quantity = randint(1, max_order_quantity)
                if fixed_quantity != None:
                    if fixed_quantity <= max_order_quantity:
                        quantity = fixed_quantity
                if long:
                    # open a position and display it
                    logging.info(dt.datetime.fromtimestamp(time()))
                    logging.info(self.client.buy_market(leverage, quantity, None, stoploss_long, takeprofit_long))
                else:
                    logging.info(dt.datetime.fromtimestamp(time()))
                    logging.info(self.client.sell_market(leverage, quantity, None, stoploss_short, takeprofit_short))
                
                # update parameters for next position
                max_quantity -= quantity
                self.client.update_order()
                long = randint(0,1)
                counter += 1
                
                # one position every 'interval' seconds
                for k in range(interval//2):
                    # collect data for the graph
                    sleep(2)
                    timestamps.append(time()- initial_timestamp)
                    user = json.loads(self.lnm.get_user())
                    balance.append(user["balance"] + user["total_running_margin"] + self.client.get_profit_and_loss())
            else:
                if show_graph:
                    # recap graph
                    return self.client.show_balance(timestamps, balance)
                return str(counter) + ' positions opened. You can consult them in Order.json file'        
        

# Simulate a random-based strategy in the past
# Output is the P&L of this strategy
    def backtest(self, initial_datetime, all_in = False, max_quantity = 20, max_leverage = 10, interval = 600):
        initial_timestamp = dt.datetime.timestamp(dt.datetime.fromisoformat(initial_datetime))

        # Other parameters you can adjust. Be carful and rescpect stoploss and takeprofit ranges.
        stoploss_long = None
        stoploss_short = None
        takeprofit_long = None
        takeprofit_short = None
        fixed_quantity = None # if you want the same quantity for each order
        fixed_leverage = None # if you want the same leverage for each order
        evaluate = True # compute the p&l you would have
        time_before_eval = 1440 # your p&l will be computed this number of minutes after position's opening
        logging.basicConfig(level=logging.INFO) # for which type of message you want to be notified

        long = randint(0,1)
        counter = 0

        if all_in:
            price = json.loads(self.lnm.futures_index_history({"to": round(1000*(initial_timestamp)), "limit": 1}))[0]["index"]
            bid_offer = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(initial_timestamp+interval*counter)), "limit": 1}))[0]
            bid = bid_offer["bid"]
            offer = bid_offer["offer"]
            if long:
                params = {
                    "type": "m",
                    "side": "b",
                    "leverage": 100,
                    "quantity": max_quantity,
                    "margin": round(10**8*max_quantity/(bid*100)),
                    "time": round(initial_timestamp),
                    "stoploss": stoploss_long,
                    "takeprofit": takeprofit_long,
                    "entry_price": bid,
                    "index_price": price,
                    "currently": "running",
                    "pl": None,
                }
            else:
                params = {
                "type": "m",
                "side": "b",
                "leverage": 100,
                "quantity": max_quantity,
                "margin": round(10**8*max_quantity/(offer*100)),
                "time": round(initial_timestamp),
                "stoploss": stoploss_short,
                "takeprofit": takeprofit_short,
                "entry_price": offer,
                "index_price": price,
                "currently": "running",
                "pl": None,
                }
            logging.info(dt.datetime.fromtimestamp(initial_timestamp))
            logging.info(' You went randomly all in. Savage !')
            self.client.store_json('Backtest.json', params)
            if evaluate:
                return self.client.evaluate_backtest('Backtest.json', initial_timestamp+time_before_eval*60)
            return ' New position opened. You can consult them in Backtest.json file'

        else: 
            while True:
                leverage = randint(1,max_leverage)
                if fixed_leverage != None:
                    leverage = fixed_leverage
                # collect previous data in LNM price history database
                sleep(2)
                price = json.loads(self.lnm.futures_index_history({"to": round(1000*(initial_timestamp+interval*counter)), "limit": 1}))[0]["index"]
                sleep(2)
                bid_offer = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(initial_timestamp+interval*counter)), "limit": 1}))[0]
                bid = bid_offer["bid"]
                offer = bid_offer["offer"]
                if max_quantity >= 1:
                    quantity = randint(1, max_quantity)
                    if fixed_quantity != None:
                        if fixed_quantity <= max_quantity:
                            quantity = fixed_quantity
                    if long:
                        params = {
                            "type": "m",
                            "side": "b",
                            "leverage": leverage,
                            "quantity": quantity,
                            "margin": round(10**8*quantity/(bid*leverage)),
                            "time": round(initial_timestamp+interval*counter),
                            "stoploss": stoploss_long,
                            "takeprofit": takeprofit_long,
                            "entry_price": bid,
                            "index_price": price,
                            "currently": "running",
                            "pl": None,
                        }
                    else:
                        params = {
                            "type": "m",
                            "side": "s",
                            "leverage": leverage,
                            "quantity": quantity,
                            "margin": round(10**8*quantity/(offer*leverage)),
                            "time": round(initial_timestamp+interval*counter),
                            "stoploss": stoploss_short,
                            "takeprofit": takeprofit_short,
                            "entry_price": offer,
                            "index_price": price,
                            "currently": "running",
                            "pl": None,
                        }
                    # position not really opened but stored in a json file
                    logging.info(dt.datetime.fromtimestamp(time()))
                    logging.info(' New random position opened')
                    self.client.store_json('Backtest.json', params)

                    counter += 1     
                    max_quantity -= quantity
                    long = randint(0,1)
                else:
                    if evaluate:
                        # evaluate the profit and loss of each position stored in json file
                        return self.client.evaluate_backtest('Backtest.json', initial_timestamp + time_before_eval*60)
                    return str(counter) + ' positions opened. You can consult them in Backtest.json file'
