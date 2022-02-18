from time import sleep, time

from lnmarkets import rest
from Lnmclient import Lnmclient

import tweepy
import json
import datetime as dt
import logging


class Twitter():


# Connection to LNMarkets and Twitter APIs
    def __init__(self, lnm_options, twitter_options):
        lnm = rest.LNMarketsRest(**lnm_options)
        lnm.futures_get_ticker()
        self.lnm = lnm
        self.twitter_client = tweepy.Client(twitter_options["bearer_token"], twitter_options["consumer_key"], twitter_options["consumer_key_secret"], twitter_options["access_token"], twitter_options["access_token_secret"], wait_on_rate_limit=True)
        self.lnm_client = Lnmclient(lnm_options)
        if len(self.twitter_client.get_me()) == 4:
            logging.info(' Connection to Twitter done')
        else:
            logging.warning('There is probably an error with your Twitter credentials')


# Return a datetime compatible with Twitter's format
    def setup_datetime(self, initial_timestamp = None, period = 60):
        if initial_timestamp == None:
            date1 = dt.datetime.now()
            # we look 'period' minutes backward (+60 min UTC)
            delta = dt.timedelta(minutes = 60 + period)
        else:
            date1 = dt.datetime.fromtimestamp(initial_timestamp)
            # we look 'period' minutes backward (already in UTC)
            delta = dt.timedelta(minutes = period)
        date2 = date1 - delta

        Y = date2.strftime('%Y')
        m = date2.strftime('%m')
        d = date2.strftime('%d')
        H = date2.strftime('%H')
        M = date2.strftime('%M')
        S = date2.strftime('%S')

        #date_format = '2001-07-21T14:30:00Z'
        date3 = Y+'-'+m+'-'+d+'T'+H+':'+M+':'+S+'Z'
        return date3


# Analyze a tweet and return BTC Fear and Greed index
    def get_fag_index(self, tweet):
        if '~ Greed' in str(tweet) or '. Greed' in str(tweet) or '- Greed'in str(tweet) or '— Greed' in str(tweet) or 'Extreme Greed' in str(tweet):
            return 1
        if '~ Fear' in str(tweet) or '. Fear' in str(tweet) or '- Fear' in str(tweet) or '— Fear' in str(tweet) or 'Extreme Fear' in str(tweet):
            return -1
        return 0


## Twitter bot looks for keywords (like 'Bitcoin') in some predefined users tweets and open a position when detecting one.
# Only one position is opened
# Inputs are detailed in Configuration file
# Output is the positon taken by the bot
    def twitter_bot(self, quantity = 20, leverage = 10, keywords = ['Bitcoin', 'bitcoin', 'BTC'], usernames_long = [], usernames_short = [], fear_and_greed = True):
        # Other parameters you can adjust. Be carful, if stoploss or takeprofit is not in the good range, your positions will not be opened.
        stoploss_long = None
        stoploss_short = None
        takeprofit_long = None
        takeprofit_short = None
        backward_period = 120 # time in minutes from which you start searching past tweets
        logging.basicConfig(level=logging.INFO) # for which type of message you want to be notified

        # get predefined users id
        id_long = []
        id_short = []
        for user in usernames_long:
            id_long.append(self.twitter_client.get_user(username = user)[0]["id"])
        for user in usernames_short:
            id_short.append(self.twitter_client.get_user(username = user)[0]["id"])

        while True:
            tweets = []
            # search tweets
            for id in id_long:
                tweets.append(self.twitter_client.get_users_tweets(id, max_results = 100, start_time = self.setup_datetime(None, backward_period))[0])
            for tweet in tweets:
                if tweet != None:
                    for k in range(len(tweet)):
                        # search keyword in tweet
                        for keyword in keywords:
                            if keyword in str(tweet[k]):
                                index = tweets.index(tweet)
                                user = usernames_long[index]
                                # display which account has tweeted and what
                                logging.info(dt.datetime.fromtimestamp(time()))
                                logging.info(user + ' has tweeted : ' + keyword)
                                # return the position opened
                                return self.lnm_client.buy_market(leverage, quantity, None, stoploss_long, takeprofit_long)

            tweets = []
            for id in id_short:
                tweets.append(self.twitter_client.get_users_tweets(id, max_results = 100, start_time = self.setup_datetime(None, backward_period))[0])
            for tweet in tweets:
                if tweet != None:
                    for k in range(len(tweet)):
                        for keyword in keywords:
                            if keyword in str(tweet[k]):
                                index = tweets.index(tweet)
                                user = usernames_short[index]
                                logging.info(dt.datetime.fromtimestamp(time()))
                                logging.info(user + 'has tweeted!' + keyword)
                                return self.lnm_client.sell_market(leverage, quantity, None, stoploss_short, takeprofit_short)

            # this bot can also open a position while looking at fear and greed index of BTC market (@BitcoinFear, id=1151046460688887808)          
            if fear_and_greed:
                tweets = self.twitter_client.get_users_tweets(1151046460688887808, max_results = 100, start_time = self.setup_datetime(None, backward_period))[0]
                if tweets != None:
                    for k in range(len(tweets)):
                        tweet = tweets[k]
                        index = self.get_fag_index(tweet)
                        if index == 1:
                            logging.info(dt.datetime.fromtimestamp(time()))
                            logging.info(' Market is greedy')
                            # if the market is greedy, the bot is greedy too and conversely
                            return self.lnm_client.buy_market(leverage, quantity, None, stoploss_long, takeprofit_long)
                        elif index == (-1):
                            logging.info(dt.datetime.fromtimestamp(time()))
                            logging.info(' Market is fearful')
                            return self.lnm_client.sell_market(leverage, quantity, None, stoploss_short, takeprofit_short)
            # wait 30 seconds before checking if a new tweet is published
            sleep(30)


# Simulate a twitter-based strategy in the past
# Only one position is opened
# Output is the P&L of this strategy
    def backtest(self, initial_datetime, quantity = 20, leverage = 10, keywords = [], usernames_long = [], usernames_short = [], fear_and_greed = True):
        initial_timestamp = dt.datetime.timestamp(dt.datetime.fromisoformat(initial_datetime))

        # Other parameters you can adjust. Be carful and rescpect stoploss and takeprofit ranges.
        stoploss_long = None
        stoploss_short = None
        takeprofit_long = None
        takeprofit_short = None
        evaluate = True # compute the p&l you would have
        time_before_eval = 60 # your p&l will be computed this number of minutes after position's opening
        logging.basicConfig(level=logging.INFO) # for which type of message you want to be notified

        id_long = []
        id_short = []
        for user in usernames_long:
            id_long.append(self.twitter_client.get_user(username = user)[0]["id"])
        for user in usernames_short:
            id_short.append(self.twitter_client.get_user(username = user)[0]["id"])
        
        while True:
            tweets = []
            for id in id_long:
                tweets.append(self.twitter_client.get_users_tweets(id, max_results = 100, start_time = self.setup_datetime(initial_timestamp), end_time = self.setup_datetime(initial_timestamp+86400), tweet_fields=['created_at'])[0])
            for tweet in tweets:
                if tweet != None:
                    for k in range(len(tweet)):
                        for keyword in keywords:
                            if keyword in str(tweet[k]):
                                creation_timestamp = dt.datetime.timestamp(tweet[k]["created_at"])
                                # collect previous data in LNM price history database
                                price = json.loads(self.lnm.futures_index_history({"to": round(1000*(creation_timestamp)), "limit": 1}))[0]["index"]
                                bid = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(creation_timestamp)), "limit": 1}))[0]["bid"]
                                params = {
                                    "type": "m",
                                    "side": "b",
                                    "leverage": leverage,
                                    "quantity": quantity,
                                    "margin": round(10**8*quantity/(bid*leverage)),
                                    "time": round(creation_timestamp),
                                    "stoploss": stoploss_long,
                                    "takeprofit": takeprofit_long,
                                    "entry_price": bid,
                                    "index_price": price,
                                    "currently": "running",                                
                                    "pl": None,
                                }
                                index = tweets.index(tweet)
                                user = usernames_long[index]
                                logging.info(user + ' has tweeted ' + keyword + ' at ' + str(tweet[k]["created_at"]))
                                # position not really opened but stored in a json file
                                self.lnm_client.store_json('Backtest.json', params)
                                if evaluate:
                                    # evaluate the profit and loss of the position stored in json file
                                    return self.lnm_client.evaluate_backtest('Backtest.json', creation_timestamp+time_before_eval*60)
                                return ' New position opened. You can consult it in Backtest.json file'
            
            tweets = []
            for id in id_short:
                tweets.append(self.twitter_client.get_users_tweets(id, max_results = 100, start_time = self.setup_datetime(initial_timestamp), end_time = self.setup_datetime(initial_timestamp+86400), tweet_fields=['created_at'])[0])
            for tweet in tweets:
                if tweet != None:
                    for k in range(len(tweet)):
                        for keyword in keywords:
                            if keyword in str(tweet[k]):
                                creation_timestamp = dt.datetime.timestamp(tweet[k]["created_at"])
                                price = json.loads(self.lnm.futures_index_history({"to": round(1000*(creation_timestamp)), "limit": 1}))[0]["index"]
                                offer = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(creation_timestamp)), "limit": 1}))[0]["offer"]
                                params = {
                                    "type": "m",
                                    "side": "s",
                                    "leverage": leverage,
                                    "quantity": quantity,
                                    "margin": round(10**8*quantity/(offer*leverage)),
                                    "time": round(creation_timestamp),
                                    "stoploss": stoploss_short,
                                    "takeprofit": takeprofit_short,
                                    "entry_price": offer,
                                    "index_price": price,
                                    "currently": "running",   
                                    "pl": None,
                                }
                                index = tweets.index(tweet)
                                user = usernames_short[index]
                                logging.info(user + ' has tweeted ' + keyword + ' at ' + str(tweet[k]["created_at"]))
                                self.lnm_client.store_json('Backtest.json', params)
                                if evaluate:
                                    return self.lnm_client.evaluate_backtest('Backtest.json', creation_timestamp+time_before_eval*60)
                                return ' New position opened. You can consult it in Backtest.json file'
                        
            if fear_and_greed:
                tweets = self.twitter_client.get_users_tweets(1151046460688887808, max_results = 100, start_time = self.setup_datetime(initial_timestamp), end_time = self.setup_datetime(initial_timestamp+86400), tweet_fields=['created_at'])[0]
                if tweets != None:
                    tweet = tweets[0]
                    creation_timestamp = dt.datetime.timestamp(tweet["created_at"])
                    index = self.get_fag_index(tweet)
                    if index == 1:
                        price = json.loads(self.lnm.futures_index_history({"to": round(1000*(creation_timestamp)), "limit": 1}))[0]["index"]
                        bid = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(creation_timestamp)), "limit": 1}))[0]["bid"]
                        params = {
                            "type": "m",
                            "side": "b",
                            "leverage": leverage,
                            "quantity": quantity,
                            "margin": round(10**8*quantity/(bid*leverage)),
                            "time": round(creation_timestamp),
                            "stoploss": stoploss_long,
                            "takeprofit": takeprofit_long,
                            "entry_price": bid,
                            "index_price": price,
                            "pl": None,
                        }
                        with open('Backtest.json', "w") as file:
                            json.dump([], file)
                        logging.info(' Market was greedy at ' + str(tweet["created_at"]))
                        self.lnm_client.store_json('Backtest.json', params)
                        if evaluate:
                            return self.lnm_client.evaluate_backtest('Backtest.json', creation_timestamp+time_before_eval*60)
                        return ' New position opened. You can consult it in Backtest.json file'
                    elif index == (-1):
                        price = json.loads(self.lnm.futures_index_history({"to": round(1000*(initial_timestamp)), "limit": 1}))[0]["index"]
                        offer = json.loads(self.lnm.futures_bid_offer_history({"to": round(1000*(initial_timestamp)), "limit": 1}))[0]["offer"]
                        params = {
                            "type": "m",
                            "side": "s",
                            "leverage": leverage,
                            "quantity": quantity,
                            "margin": round(10**8*quantity/(offer*leverage)),
                            "time": round(creation_timestamp),
                            "stoploss": stoploss_short,
                            "takeprofit": takeprofit_short,
                            "entry_price": offer,
                            "index_price": price,
                            "pl": None,
                        }
                        with open('Backtest.json', "w") as file:
                            json.dump([], file)
                        logging.info(' Market was fearful at ' + str(tweet["created_at"]))
                        self.lnm_client.store_json('Backtest.json', params)
                        if evaluate:
                            return self.lnm_client.evaluate_backtest('Backtest.json', creation_timestamp+time_before_eval*60)
                        return ' New position opened. You can consult it in Backtest.json file'
            # search an interesting tweet one day later
            initial_timestamp += 86400
