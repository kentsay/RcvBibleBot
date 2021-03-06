import os
import configparser
from itertools import chain

APP_ENV = os.environ.get('APP_ENV') or 'local'  # or 'prod' to load production
INI_FILE = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        './conf/{}.ini'.format(APP_ENV))

CONFIG = configparser.ConfigParser()
CONFIG.read(INI_FILE)

REDIS_URL  = CONFIG.get("redis", "host")
REDIS_PORT = CONFIG.get("redis", "port")
REDIS_DB   = CONFIG.get("redis", "db")

LOG_LEVEL  = CONFIG.get("logging", "level")

API_URL = CONFIG.get("lsmapi", "url")
API_FORMAT = CONFIG.get("lsmapi", "format")
