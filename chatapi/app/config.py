import os
import ConfigParser
from itertools import chain

BRAND_NAME = 'Recovery Version Bible Facebook Messenger Bot'

APP_ENV = os.environ.get('APP_ENV') or 'local'  # or 'prod' to load production
INI_FILE = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        '../conf/{}.ini'.format(APP_ENV))

CONFIG = ConfigParser.ConfigParser()
CONFIG.read(INI_FILE)

REDIS_URL  = CONFIG.get("redis", "host")
REDIS_PORT = CONFIG.get("redis", "port")
REDIS_DB   = CONFIG.get("redis", "db")

LOG_LEVEL  = CONFIG.get("logging", "level")

FB_MESSAGE_URL = CONFIG.get("facebook", "fb_message_url")
FB_TOKEN = CONFIG.get("facebook", "token")
FB_ACCESS_TOKEN = CONFIG.get("facebook", "access_token")
