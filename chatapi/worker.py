#worker.py

import os
import redis
import config
from rq import Worker, Queue, Connection

"""RQ workers listen to fb_message queue."""
listen = ['fb_message']
redis_url = os.getenv('REDISTOGO_URL', 'redis://'+ config.REDIS_URL + ':' + config.REDIS_PORT)

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
