import yaml


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


config_file = 'config.yml'
config = load_config(config_file)
