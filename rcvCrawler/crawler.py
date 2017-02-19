# crawler.py

import re
import redis
from rq import Queue
from rq.job import Job

import config
import log
from bible_re import testaments
from lsmHandler import verseProcessor

LOG = log.get_logger()

try:
    pool = redis.ConnectionPool(host=config.REDIS_URL, port=config.REDIS_PORT, db=config.REDIS_DB)
    rd = redis.Redis(connection_pool=pool)
except Exception as ex:
    print ex

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
            """
            Enqueueing api request as jobs into lsm_rcv_api queue
            and processing them in the background with workers.
            """
            q = Queue('lsm_rcv_api', connection=rd)
            job = q.enqueue_call(
                func=verseProcessor, args=(query,), result_ttl=5000
            )
            LOG.info('lsm-api request ' + str(job.get_id()))
