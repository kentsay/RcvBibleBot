# search.py

import falcon
import string
import json
from app import log
from app.database import redis_db
from app.util.stringUtil import preProcess
from app.errors import AppError, InvalidParameterError

LOG = log.get_logger()

class BibleResoure(object):

    def __init__(self, db):
        self.db = db

    # This function handles GET reuqests
    def on_get(self, req, resp):
        try:
            db = redis_db.RedisStorageEngine()
            r = db.connection()
        except Exception as ex:
            print ex

        resp.body = json.dumps("Hello")
        resp.status = falcon.HTTP_200  # This is the default status
