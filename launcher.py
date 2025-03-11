from strategies.ta_summary import TAS
from config_loader import yaml_file, lnm_options

# call the bot you have choosed in configuration file
def bot():
    if yaml_file['strategies']['ta_summary']:
        config = yaml_file['ta_summary']
        return TAS.ta_summary(TAS(lnm_options), 
                                    quantity = config['quantity'], 
                                    leverage = config['leverage'],
                                    takeprofit = config['takeprofit'],
                                    stoploss = config['stoploss'],
                                    interval = config['interval'], 
                                    timeout = config['timeout'])
