from time import sleep, time

from lnmarkets import rest

import json
import datetime as dt
import matplotlib.pyplot as plt
import logging

logging.basicConfig(level=logging.INFO)


class Lnmclient():


# Connection to LNMarkets API and verification that the authentication works porperly
    def __init__(self, options):
        lnm = rest.LNMarketsRest(**options)
        lnm.futures_get_ticker()
        self.lnm = lnm
        with open('Order.json', "w") as file:
            json.dump([], file)
        with open('Backtest.json', "w") as file:
            json.dump([], file)
        if len(json.loads(self.lnm.get_user())) != 28:
            logging.warning(' There is probably an error with your LNM credentials')
        else:
            logging.info(' Connection to LN Markets done')


# To add some optional parameters to an order
    def new_params(self, params, quantity, margin, stoploss, takeprofit):
        if quantity != None:
            params["quantity"] = quantity
        if margin != None:
            params["margin"] = margin
        if stoploss != None:
            params["stoploss"] = stoploss
        if takeprofit != None:
            params["takeprofit"] = takeprofit
        return params

# To add some optional parameters to the order recap
    def store_params(self, params, pos):
        params["pid"] = pos["position"]["pid"]
        if params["type"] == "m":
            params["currently"] = "running"
        else:
            params["currently"] = "open"
        params["entry_price"] = pos["position"]["price"]
        params["exit_price"] = pos["position"]["exit_price"]
        return params
    
## Opening positions
# Open immediatly a long position and store the parameters in Order.json recap file
    def buy_market(self, leverage, quantity=None, margin=None, stoploss=None, takeprofit=None):
        params = {
            "type": "m",
            "side": "b",
            "leverage": leverage
        }
        params = self.new_params(params, quantity, margin, stoploss, takeprofit)
        pos = json.loads(self.lnm.futures_new_position(params))
        params = self.store_params(params, pos)
        self.store_json('Order.json', params)
        return pos

    def buy_limit(self, price, leverage, quantity=None, margin=None, stoploss=None, takeprofit=None):
        params = {
                "type": "l",
                "side": "b",
                "leverage": leverage,
                "price": price
            }
        params = self.new_params(params, quantity, margin, stoploss, takeprofit)
        pos = json.loads(self.lnm.futures_new_position(params))
        params = self.store_params(params, pos)
        self.store_json('Order.json', params)
        return pos

    def sell_market(self, leverage, quantity=None, margin=None, stoploss=None, takeprofit=None):
        params = {
            "type": "m",
            "side": "s",
            "leverage": leverage
        }
        params = self.new_params(params, quantity, margin, stoploss, takeprofit)
        pos = json.loads(self.lnm.futures_new_position(params))
        params = self.store_params(params, pos)
        self.store_json('Order.json', params)
        return pos

    def sell_limit(self, price, leverage, quantity=None, margin=None, stoploss=None, takeprofit=None):
        params = {
                "type": "l",
                "side": "s",
                "leverage": leverage,
                "price": price
            }
        params = self.new_params(params, quantity, margin, stoploss, takeprofit)
        pos = json.loads(self.lnm.futures_new_position(params))
        params = self.store_params(params, pos)
        self.store_json('Order.json', params)
        return pos

# Recreate the All In button available on LN Markets website
    def buy_all_in(self):
        total_amount = json.loads(self.lnm.get_user())["balance"]
        params = {
                "type": "m",
                "side": "b",
                "leverage": 100,
            }
        params = self.new_params(params, None, total_amount, None, None)
        pos = json.loads(self.lnm.futures_new_position(params))
        params = self.store_params(params, pos)
        self.store_json('Order.json', params)
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.warning(' You went all in !')
        return pos

    def sell_all_in(self):
        total_amount = json.loads(self.lnm.get_user())["balance"]
        params = {
                "type": "m",
                "side": "s",
                "leverage": 100,
            }
        params = self.new_params(params, None, total_amount, None, None)
        pos = json.loads(self.lnm.futures_new_position(params))
        params = self.store_params(params, pos)
        self.store_json('Order.json', params)
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.warning(' You went all in !')
        return pos


## Cancel or close positions
    def cancel_position(self, pid):
        position = json.loads(self.lnm.futures_cancel_position({"pid": pid}))
        f = self.load_json('Order.json')
        for pos in f:
            if pos["pid"] == pid:
                pos["exit_price"] = position["position"]["exit_price"]
                pos["currently"] = "canceled"
        with open('Order.json', "w") as outfile:
            json.dump(f, outfile, indent = 1)
        return position

    def close_position(self, pid):
        position = json.loads(self.lnm.futures_close_position({"pid": pid}))
        f = self.load_json('Order.json')
        for pos in f:
            if pos["pid"] == pid:
                pos["exit_price"] = position["position"]["exit_price"]
                pos["currently"] = "closed"
        with open('Order.json', "w") as outfile:
            json.dump(f, outfile, indent = 1)
        return position

    def is_long(self, position): 
        if position["side"] == "b":
            return True
        return False

    def cancel_all_longs(self):
        positions = json.loads(self.lnm.futures_get_positions({"type": "open"}))
        for pos in positions:
            if self.is_long(pos):
                self.cancel_position(pos["pid"])
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.info(' All longs canceled')

    def cancel_all_shorts(self):
        positions = json.loads(self.lnm.futures_get_positions({"type": "open"}))
        for pos in positions:
            if not self.is_long(pos):
                self.cancel_position(pos["pid"])
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.info(' All shorts canceled')

    def close_all_longs(self):
        positions = json.loads(self.lnm.futures_get_positions({"type": "running"}))
        for pos in positions:
            if self.is_long(pos):
                self.close_position(pos["pid"])
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.info(' All longs closed')

    def close_all_shorts(self):
        positions = json.loads(self.lnm.futures_get_positions({"type": "running"}))
        for pos in positions:
            if not self.is_long(pos):
                self.close_position(pos["pid"])
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.info(' All shorts closed')

    def cancel_all_positions(self):
        positions = json.loads(self.lnm.futures_get_positions({"type": "open"}))
        for pos in positions:
            self.cancel_position(pos["pid"])
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.info(' All positions canceled')

    def close_all_positions(self):
        positions = json.loads(self.lnm.futures_get_positions({"type": "running"}))
        for pos in positions:
            self.close_position(pos["pid"])
        logging.info(dt.datetime.fromtimestamp(time()))
        logging.info(' All positions closed')

    def update_order(self):
        open_positions = json.loads(self.lnm.futures_get_positions({"type": "open"}))
        running_positions = json.loads(self.lnm.futures_get_positions({"type": "running"}))
        closed_positions = json.loads(self.lnm.futures_get_positions({"type": "closed"}))
        f = self.load_json('Order.json')
        for pos in f:
            for k in range(len(open_positions)):
                if pos["pid"] == open_positions[k]["pid"]:
                    pos["currently"] = "open"
            for k in range(len(running_positions)):
                if pos["pid"] == running_positions[k]["pid"]:
                    pos["currently"] = "running"
            for k in range(len(closed_positions)):
                if pos["pid"] == closed_positions[k]["pid"]:
                    pos["currently"] = "closed"
                    pos["exit_price"] = closed_positions[k]["exit_price"]
        with open('Order.json', "w") as outfile:
            json.dump(f, outfile, indent = 1)



## Additional methods
# To add or modify a stoploss or a takeprofit
    def update_position(self, pid, type, price):
        position = json.loads(self.lnm.futures_update_position({
            "pid": pid,
            "type": type,
            "value": price,
        }))
        f = self.load_json('Order.json')
        for pos in f:
            if pos["pid"] == pid:
                pos[type] = price
        with open('Order.json', "w") as outfile:
            json.dump(f, outfile, indent = 1)
        return position

    def add_margin(self, pid, amount):
        position = json.loads(self.lnm.futures_add_margin_position({
            "pid": pid,
            "amount": amount,
        }))
        f = self.load_json('Order.json')
        for pos in f:
            if pos["pid"] == pid:
                pos["margin"] += amount
                pos["pid"] = position["pid"]
        with open('Order.json', "w") as outfile:
            json.dump(f, outfile, indent = 1)
        return position

    def cash_in(self, pid, amount):
        position = json.loads(self.lnm.futures_cashin_position({
            "pid": pid,
            "amount": amount,
        }))
        f = self.load_json('Order.json')
        for pos in f:
            if pos["pid"] == pid:
                pos["margin"] -= amount
                pos["pid"] = position["pid"]
        with open('Order.json', "w") as outfile:
            json.dump(f, outfile, indent = 1)
        return position

# compute the P&L of all running positions
    def get_profit_and_loss(self):
        pl = 0
        positions = json.loads(self.lnm.futures_get_positions({'type': 'running'}))
        for pos in positions:
            pl += pos['pl']
        return pl


## Functions used to treat json files
# Open and read json
    def load_json(self, file):
        with open(file, 'r+') as f:
            return json.load(f)

# Open and write json
    def store_json(self, file, order):
        f = self.load_json(file)
        f.append(order)
        with open(file, "w") as outfile:
            json.dump(f, outfile, indent = 1)


# Graph of balance evolution during bot execution
    def show_balance(self, timestamps, balance):
        plt.figure('Balance history')
        plt.title('Evolution of Balance')
        plt.grid()
        plt.plot(timestamps, balance, "k-", linewidth=1)
        if min(balance)-(max(balance)-min(balance))/4 - max(balance)+(max(balance)-min(balance))/4 <=100:
            y_mini = (min(balance)+max(balance))/2-50
            y_maxi = (min(balance)+max(balance))/2+50
            plt.ylim(y_mini, y_maxi)
        else:
            y_mini = min(balance)-(max(balance)-min(balance))/4-50
            y_maxi = max(balance)+(max(balance)-min(balance))/4+50
            plt.ylim(y_mini, y_maxi)
        plt.xlabel('Time (sec)', size=14)
        plt.ylabel('Balance (sats)', size=14)
        plt.show()

    
# when backtesting a strategy, check if a position has been closed before the end
    def early_closure(self, pos, bid, offer):
        if pos["pl"] == None:
            if pos["side"] == "b":
                if pos["takeprofit"] != None:
                    if bid >= pos["takeprofit"]: #takeprofit
                        pos["pl"] = (1/pos["entry_price"] - 1/bid) * pos["quantity"]
                        pos["exit_price"] = bid
                        pos["currently"] = "close"
                if pos["stoploss"] != None:
                    if bid <= pos["stoploss"]: #stoploss
                        pos["pl"] = (1/pos["entry_price"] - 1/bid) * pos["quantity"]
                        pos["exit_price"] = bid
                if bid <= pos["entry_price"] * 1 / (1 + 1/pos["leverage"]): #liquidation
                    pos["pl"] = 0
                    pos["exit_price"] = bid
            else:
                if pos["takeprofit"] != None:
                    if offer <= pos["takeprofit"]: #takeprofit
                        pos["pl"] = -(1/pos["entry_price"] - 1/offer) * pos["quantity"]
                        pos["exit_price"] = offer
                        pos["currently"] = "close"
                if pos["stoploss"] != None:
                    if offer >= pos["stoploss"]: #stoploss
                        pos["pl"] = -(1/pos["entry_price"] - 1/offer) * pos["quantity"]
                        pos["exit_price"] = offer
                        pos["currently"] = "close"
                if pos["leverage"] != 1: #liquidation
                    if offer >= pos["entry_price"] * 1 / (1 - 1/pos["leverage"]):
                        pos["pl"] = 0
                        pos["exit_price"] = offer
                        pos["currently"] = "close"
        return pos


## Compute the result (P&L) of a backtested strategy
# inputs are a file (Backtest.json) with all the orders simulated by the bot, and a timestamp which corresponds to the moment when the P&L is computed
# output is the P&L in sats (int)
    def evaluate_backtest(self, json_file, final_timestamp):
        # checking all the prices histories to be sure that a position have not been liquidated is long
        logging.warning('Backtesting in progress. These computations may last few minutes.')
        pl = 0
        file = self.load_json(json_file)
        initial_timestamp = file[0]["time"]
        # accuracy is adapted depending backtesting's duration
        step = int((final_timestamp - initial_timestamp) // 40)

        for t in range(initial_timestamp, round(final_timestamp), step):
            # wait is mandatory to respect LNMarkets API requests limits
            sleep(2)
            bid_offer = json.loads(self.lnm.futures_bid_offer_history({"to": 1000*t, "limit": 1}))[0]
            bid = bid_offer["bid"]
            offer = bid_offer["offer"]

            # check liquidation, stoploss and takeprofit
            for pos in file:
                self.early_closure(pos, bid, offer)

        for pos in file:
            if pos["pl"] == None:
                final_bid_offer = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*final_timestamp), "limit": 1}))[0]
                final_bid = final_bid_offer["bid"]
                final_offer = final_bid_offer["offer"]
                if pos["side"] == "b":
                    pos["pl"] = (1/pos["entry_price"] - 1/final_bid) * pos["quantity"]
                else:
                    pos["pl"] = -(1/pos["entry_price"] - 1/final_offer) * pos["quantity"]
            pos["pl"] *= 10**8 # conversion in sats
            pl += pos["pl"]
        
        with open('Backtest.json', "w") as outfile:
            json.dump(file, outfile, indent = 1)
        return 'profit & loss backtest = ' + str(round(pl)) + ' sats.'

