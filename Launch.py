from Strategies.Random import Random
from Strategies.Twitter import Twitter
from Strategies.Ema import Ema

import yaml


# To load Configuration.yml file
def load_yaml(file):
    with open(file) as file:
        load = yaml.load(file, Loader=yaml.FullLoader)
    return load

yaml_file = load_yaml('./Configuration.yml')

lnm_options = yaml_file["lnm_credentials"]
twitter_options = yaml_file["twitter_credentials"]


# call the bot you have choosed in Configuration file
def bot():
    if yaml_file["Strategies"]["Random"]:
        config = yaml_file["Random"]
        return Random.random_bot(Random(lnm_options), config["all_in"], config["max_quantity"], config["max_leverage"], config["interval"])

    elif yaml_file["Strategies"]["Random_Backtest"]:
        config = yaml_file["Random_Backtest"]
        return Random.backtest(Random(lnm_options), config["initial_datetime"], config["all_in"], config["max_quantity"], config["max_leverage"], config["interval"])

    elif yaml_file["Strategies"]["Twitter"]:
        config = yaml_file["Twitter"]
        return Twitter.twitter_bot(Twitter(lnm_options, twitter_options), config["quantity_per_order"], config['leverage'], config["keywords"], config["usernames_long"], config['usernames_short'], config["fear_and_greed"])

    elif yaml_file["Strategies"]["Twitter_Backtest"]:
        config = yaml_file["Twitter_Backtest"]
        return Twitter.backtest(Twitter(lnm_options, twitter_options), config["initial_datetime"], config["quantity_per_order"], config['leverage'], config["keywords"], config["usernames_long"], config['usernames_short'], config["fear_and_greed"])

    elif yaml_file["Strategies"]["Ema"]:
        config = yaml_file["Ema"]
        return Ema.ema_bot(Ema(lnm_options), config["quantity_per_order"], config["leverage"], config["little_period"], config["big_period"], config["time_scale"])

    elif yaml_file["Strategies"]["Ema_Backtest"]:
        config = yaml_file["Ema_Backtest"]
        return Ema.backtest(Ema(lnm_options), config["initial_datetime"], config["quantity_per_order"], config["leverage"], config["little_period"], config["big_period"], config["time_scale"])
