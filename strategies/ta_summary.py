import json
import logging
import os
from time import time, sleep

import pandas as pd
from tradingview_ta import TA_Handler, Interval

from lnm_client import lnm_client
from config_loader import yaml_file

logging.basicConfig(level=logging.INFO)

operate = yaml_file.get("operate", True)

def process_long(self, quantity, leverage, takeprofit, stoploss, id_list):
    last = json.loads(self.lnm.get_last())['lastPrice']
    tp = round(last * (1 + takeprofit))
    sl = round(last * (1 - stoploss))

    if not operate:
        self.lnm.market_long(quantity=quantity, leverage=leverage, takeprofit=tp, stoploss=sl)
        return

    # logging.debug(self.lnm.market_long(quantity=quantity, leverage=leverage, takeprofit=tp, stoploss=sl))
    operation_id = json.loads(self.lnm.market_long(quantity=quantity, leverage=leverage, takeprofit=tp, stoploss=sl))[
        'id']
    id_list.append(operation_id)


def process_short(self, quantity, leverage, takeprofit, stoploss, id_list):
    last = json.loads(self.lnm.get_last())['lastPrice']
    tp = round(last * (1 - takeprofit))
    sl = round(last * (1 + stoploss))

    if not operate:
        self.lnm.market_short(quantity=quantity, leverage=leverage, takeprofit=tp, stoploss=sl)
        return

    self.lnm.market_short(quantity=quantity, leverage=leverage, takeprofit=tp, stoploss=sl)
    operation_id = json.loads(self.lnm.market_short(quantity=quantity, leverage=leverage, takeprofit=tp, stoploss=sl))[
        'id']
    id_list.append(operation_id)


class TAS:
    # Connection to LNMarkets API
    def __init__(self, options):
        self.options = options
        self.lnm = lnm_client(self.options)

    def process_close(self, operation_id, id_list):

        if not operate:
            self.lnm.close_position(operation_id)
            return

        self.lnm.close_position(operation_id)
        # remove the id from the list
        id_list.remove(operation_id)

    # Get trading signal from trading view https://www.tradingview.com/symbols/XBTUSD/technicals/
    def get_ta(symbol, screener, exchange, interval):
        interval_list = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d', '1W', '1M']
        ta_interval_list = [Interval.INTERVAL_1_MINUTE,
                            Interval.INTERVAL_5_MINUTES,
                            Interval.INTERVAL_15_MINUTES,
                            Interval.INTERVAL_30_MINUTES,
                            Interval.INTERVAL_1_HOUR,
                            Interval.INTERVAL_2_HOURS,
                            Interval.INTERVAL_4_HOURS,
                            Interval.INTERVAL_1_DAY,
                            Interval.INTERVAL_1_WEEK,
                            Interval.INTERVAL_1_MONTH]

        ta_interval = ta_interval_list[interval_list.index(interval)]

        return TA_Handler(
            symbol=symbol,
            screener=screener,
            exchange=exchange,
            interval=ta_interval,
        ).get_analysis().summary

    # Output can be a graph showing the evolution of your Balance during the strategy
    def ta_summary(self, quantity, leverage, takeprofit, stoploss, interval, timeout):
        symbol = 'BTCUSD.P'
        screener = 'CRYPTO'
        exchange = 'BITMEX'

        interval_list = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '1d', '1W', '1M']
        t_interval_list = [60, 300, 900, 1800, 3600, 7200, 14400, 86400, 604800, 2592000]
        t_interval = t_interval_list[interval_list.index(interval)]

        timeout = time() + 60 * timeout

        id_list = []
        try:
            logging.debug(f"DEBUG - Chamada para get_ta() com symbol={symbol}, exchange={exchange}")
            analysis = TAS.get_ta(symbol, screener, exchange, interval)
        except Exception as e:
            logging.warning(f"Erro ao obter análise do TradingView: {e}")
            sleep(10)

        logging.info(analysis)
        if analysis['RECOMMENDATION'] == 'STRONG_BUY':
            side = 'long'
            process_long(self, quantity, leverage, takeprofit, stoploss, id_list)

        elif analysis['RECOMMENDATION'] == 'STRONG_SELL':
            side = 'short'
            process_short(self, quantity, leverage, takeprofit, stoploss, id_list)
        else:
            side = 'neutral'

        sleep(t_interval)

        while True:
            try:
                logging.debug(f"DEBUG - Chamada para get_ta() com symbol={symbol}, exchange={exchange}")
                analysis = TAS.get_ta(symbol, screener, exchange, interval)
            except Exception as e:
                logging.warning(f"Erro ao obter análise do TradingView: {e}")
                sleep(10)

            logging.info(analysis)

            num_pos_running = len(json.loads(self.lnm.get_trades(type_trade='running')))
            id_running = [json.loads(self.lnm.get_trades(type_trade='running'))[i]['id'] for i in
                          range(num_pos_running)]

            if len(id_running) > 0 and len(id_list) > 0:  # If there are running positions and positions in the list
                for id in id_list:  # For each position in the list of positions that have been opened by the bot
                    if side == 'long':
                        if 'BUY' in analysis['RECOMMENDATION']:
                            logging.info('Keep long open')
                        elif analysis['RECOMMENDATION'] == 'STRONG_SELL':
                            self.process_close(id, id_list)
                            side = 'short'
                            process_short(self, quantity, leverage, takeprofit, stoploss, id_list)
                        else:
                            self.process_close(id, id_list)
                            side = 'neutral'
                    elif side == 'short':
                        if 'SELL' in analysis['RECOMMENDATION']:
                            logging.info('Keep short open')
                        elif analysis['RECOMMENDATION'] == 'STRONG_BUY':
                            self.process_close(id, id_list)
                            side = 'long'
                            process_long(self, quantity, leverage, takeprofit, stoploss, id_list)
                        else:
                            self.process_close(id, id_list)
                            side = 'neutral'
                    elif side == 'neutral':
                        if analysis['RECOMMENDATION'] == 'STRONG_BUY':
                            side = 'long'
                            process_long(self, quantity, leverage, takeprofit, stoploss, id_list)

                        elif analysis['RECOMMENDATION'] == 'STRONG_SELL':
                            side = 'short'
                            process_short(self, quantity, leverage, takeprofit, stoploss, id_list)
                        else:
                            side = 'neutral'
                            logging.info('Stay neutral')

            else:
                if analysis['RECOMMENDATION'] == 'STRONG_BUY':
                    side = 'long'
                    process_long(self, quantity, leverage, takeprofit, stoploss, id_list)

                elif analysis['RECOMMENDATION'] == 'STRONG_SELL':
                    side = 'short'
                    process_short(self, quantity, leverage, takeprofit, stoploss, id_list)
                else:
                    side = 'neutral'

            if time() > timeout:
                break

            logging.debug(id_list)
            sleep(t_interval)

        for operation_id in id_list:
            self.process_close(operation_id, id_list)
            id_list.append(operation_id)

        closed_positions = json.loads(self.lnm.get_trades(type_trade='closed'))
        df_closed_positions = pd.DataFrame.from_dict(closed_positions)

        df_closed_pos = df_closed_positions[df_closed_positions['id'].isin(id_list)].copy()

        pl = df_closed_pos['pl'].sum()

        logging.info('Total PL (sats) = ' + str(pl))

        path = os.path.join(os.path.dirname(__file__), "df_closed_pos.csv")
        df_closed_pos.to_csv(path)
        logging.info('df_closed_pos.csv saved in strategies folder')
