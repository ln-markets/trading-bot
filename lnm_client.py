from lnmarkets import rest
import datetime
from time import time
import logging
import json
from config_loader import yaml_file

logging.basicConfig(level=logging.INFO)

operate = yaml_file.get("operate", True)

class lnm_client():
    # Connection to LN Markets API
    def __init__(self, options):
        self.options = options
        self.lnm = rest.LNMarketsRest(**self.options)
        if len(json.loads(self.lnm.get_user())['uid']) != 36:
            logging.warning('There is probably an error with your LN Markets credentials')
        else:
            logging.info('Connection to LN Markets ok!')

    def get_user(self):
        print(self.lnm.get_user())

    def market_long(self, quantity, leverage, takeprofit, stoploss):
        params = {
            'type': 'm',
            'side': 'b',
            'quantity': quantity,
            'leverage': leverage,
            'takeprofit': takeprofit,
            'stoploss': stoploss
        }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(
            f'New Market Buy Running for Quantity = {quantity}, leverage = {leverage}, take profit = {takeprofit}, stop loss = {stoploss}')

        if not operate:
            logging.debug("🚫 Blocked call (`operate: false` no configuration.yml)")
            return {}

        return self.lnm.futures_new_trade(params)

    def market_short(self, quantity, leverage, takeprofit, stoploss):
        params = {
            'type': 'm',
            'side': 's',
            'quantity': quantity,
            'leverage': leverage,
            'takeprofit': takeprofit,
            'stoploss': stoploss
        }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(
            f'New Market Sell Running for Quantity = {quantity}, leverage = {leverage}, take profit = {takeprofit}, stop loss = {stoploss}')

        if not operate:
            logging.debug("🚫 Blocked call (`operate: false` no configuration.yml)")
            return {}

        return self.lnm.futures_new_trade(params)

    def close_position(self, operation_id):
        params = {
            'id': operation_id,
        }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(f'Close position id = {operation_id}')

        if not operate:
            logging.debug("🚫 Blocked call (`operate: false` no configuration.yml)")
            return {}

        return self.lnm.futures_close(params)

    def get_last(self):
        return self.lnm.futures_get_ticker()

    def get_trades(self, type_trade):
        params = {
            'type': type_trade,
        }
        return self.lnm.futures_get_trades(params)
