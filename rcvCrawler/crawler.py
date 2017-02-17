import config
from bible_re import book_re_string, testaments
import re
import requests
import redis
import json
import string
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
            sleep(1)
            query = "%s%d:%d" %(target,i+1,j)
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
            rd.sadd(query, result)
            """
            Since we cannot query on document of a document index, you have to manually build and maintain document indexes.
            """
            tokens = result.split(" ")
            for token in tokens:
                """
                Strip punctuation from string and convert into lower case.
                otherwise 'Do' and 'do' will be 2 different keywords.
                """
                token = token.strip(string.punctuation).lower()
                """
                SADD: Add the specified members to the set stored at key. Specified members that are already a member of this set are ignored.
                """
                rd.sadd(token, query)
