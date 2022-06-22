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
        logging.info(f'New Market Buy Running for Quantity = {quantity}, leverage = {leverage}, take profit = {takeprofit}, stop loss = {stoploss}')
        return self.lnm.futures_new_position(params)

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
        logging.info(f'New Market Sell Running for Quantity = {quantity}, leverage = {leverage}, take profit = {takeprofit}, stop loss = {stoploss}')
        return self.lnm.futures_new_position(params)
    
    
    def close_position(self, pid):
        params = {
            'pid': pid,
            }
        logging.info(datetime.datetime.fromtimestamp(time()))
        logging.info(f'Close position pid = {pid}')

        return self.lnm.futures_close_position(params)

    def get_positions(self, type_pos):
        params = {
            'type': type_pos,
            }
        return self.lnm.futures_get_positions(params)

    def get_bid_offer(self):
        return self.lnm.futures_get_ticker()

    


# options = {
#     'key': 'dR2dnom1oMljsN33DJjxNA7bSvItEg82sdZ00HjxY7s=',
#     'secret': '4VW5Zp5K4DqOZC8Zr4jd2dw5Bi/G8nxs9qEK3fQ7aIVGrzjsczMpbZQonKoe89N+V3MwFdUHoYn1ydh7eHf5Rg==',
#     'passphrase': 'dg05hcihaci8f',
#     'network': 'testnet'}

# lnm = lnm_client(options)


# lnm.close_position(pid='2729a816-f22c-4488-a29b-972f67cee967')
# lnm.market_long(quantity = 10, leverage = 10, takeprofit = 25000, stoploss = 20000)
# print(json.loads(lnm.get_bid_offer())['offer'])
