import configparser


class Utils:
    @staticmethod
    def read_config_data(section: str):
        # read database config from config file
        config = configparser.ConfigParser()
        config.read('../config.ini')
        return dict(config.items(section))
