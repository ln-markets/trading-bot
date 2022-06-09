from lnmarkets import rest
import datetime
from time import time
import logging
import json

logging.basicConfig(level=logging.INFO)


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


    def market_long(self, quantity, leverage):
        params = {
            'type': 'm',
            'side': 'b',
            'quantity': quantity,
            'leverage': leverage
        }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(f'New Market Buy Running for Quantity = {quantity} and Leverage = {leverage}')
        return self.lnm.futures_new_position(params)

    def market_short(self, quantity, leverage):
        params = {
            'type': 'm',
            'side': 's',
            'quantity': quantity,
            'leverage': leverage
        }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(f'New Market Sell Running for Quantity = {quantity} and Leverage = {leverage}')
        return self.lnm.futures_new_position(params)
    
    
    def close_position(self, pid):
        params = {
            'pid': pid,
            }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(f'Close position pid = {pid}')

        return self.lnm.futures_close_position(params)

    def get_positions(self):
        params = {
            'type': 'closed',
            }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info('Retrieving closed positions')

        return self.lnm.futures_get_positions(params)


# options = {
#     'key': 'qE8nObMFzyEHd5moHZxBY7LeYkxVQrH8VxEsLHVI9Sw=',
#     'secret': 'Z7oTS5WtsmBqp1ysg46RSQ7Wtt9xP7ANC4z0NZaETKBWo74rZXZqEKynpfKyf5gKU0R3xWVn1DrSljA5LXqSUw==',
#     'passphrase': '8eehc19ghfc97',
#     'network': 'testnet'}

# lnm = lnm_client(options)

# #lnm.close_position(pid='2729a816-f22c-4488-a29b-972f67cee967')

# lnm.market_long(quantity = 10, leverage = 10)