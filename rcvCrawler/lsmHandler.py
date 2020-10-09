#lsmHandler

import json
import string
import requests
import redis

import config
import log

LOG = log.get_logger()

try:
    pool = redis.ConnectionPool(host=config.REDIS_URL, port=config.REDIS_PORT, db=config.REDIS_DB)
    rd = redis.Redis(connection_pool=pool)
except Exception as ex:
    print (ex)

def verseProcessor(query):
    black_list = ['Mark9:44', 'Mark9:46', 'Rom.16:24']
    if query not in black_list:
        r = requests.get(config.API_URL + query + config.API_FORMAT)
        try:
            verse_json = json.loads(r.text, encoding='utf-8')
        except ValueError:
            LOG.error('Malformed JSON: Could not decode the request body. The JSON was incorrect')

        result = verse_json['verses'][0].get('text')
        LOG.info('Process: ' + query)

    else:
        LOG.info('Process: ' + query)
        if query == 'Mark9:44':
            result = 'See note 44-1'
        if query == 'Mark9:46':
            result = 'See note 46-1'
        if query == 'Rom.16:24':
            result = 'See note 24-1'

    """Add verses into Redis"""
    if len(rd.smembers(query)) == 0:
        rd.sadd(query, result)
    else:
        rd.spop(query)
        rd.sadd(query, result)
