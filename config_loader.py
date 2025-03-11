import os
import yaml

# To load configuration.yml file
def load_yaml(file):
    with open(file) as file:
        load = yaml.load(file, Loader=yaml.FullLoader)
    return load

yaml_file = load_yaml(os.path.join(os.path.dirname(__file__), "configuration.yml"))
lnm_options = yaml_file["lnm_credentials"]
