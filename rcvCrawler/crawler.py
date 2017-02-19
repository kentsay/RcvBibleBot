import config
from bible_re import book_re_string, testaments
import re
import requests
import redis
import json
import string
import falcon
from time import sleep

pool = redis.ConnectionPool(host=config.REDIS_URL, port=config.REDIS_PORT, db=config.REDIS_DB)
rd = redis.Redis(connection_pool=pool)

def get_book(name):
    """
    Get a book from its name or None if not found
    """
    for books in testaments.itervalues():
        for book in books:
            if re.match(book[2], name, re.IGNORECASE):
                return book
    return None

targets = []
for books in testaments.itervalues():
    for book in books:
        targets.append(book[1])

for target in targets:
    book = get_book(target)
    for i in range(0, len(book[3])):
        for j in range (1, book[3][i]+1):
            query = "%s%d:%d" %(target,i+1,j)
            black_list = ['Mark9:44', 'Mark9:46', 'Rom.16:24']
            if query not in black_list:
                r = requests.get(config.API_URL + query + config.API_FORMAT)
                try:
                    verse_json = json.loads(r.text, encoding='utf-8')
                except ValueError:
                    raise falcon.HTTPError(falcon.HTTP_400,
                        'Malformed JSON',
                        'Could not decode the request body. The JSON was incorrect.')

                result = verse_json['verses'][0].get('text')
                print result
                """Add/update verses"""
                if len(rd.smembers(query)) == 0:
                    rd.sadd(query, result)
                else:
                    rd.spop(query)
                    rd.sadd(query, result)
