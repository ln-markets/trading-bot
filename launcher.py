from strategies.ta_summary import TAS
import os
import yaml


# To load Configuration.yml file
def load_yaml(file):
    with open(file) as file:
        load = yaml.load(file, Loader=yaml.FullLoader)
    return load

yaml_file = load_yaml(os.path.join(os.path.dirname(__file__), "configuration.yml"))

lnm_options = yaml_file["lnm_credentials"]

# call the bot you have choosed in configuration file
def bot():
    if yaml_file['strategies']['ta_summary']:
        config = yaml_file['ta_summary']
        return TAS.ta_summary(TAS(lnm_options), 
                                    quantity = config['quantity'], 
                                    leverage = config['leverage'], 
                                    interval = config['interval'], 
                                    timeout = config['timeout'])
