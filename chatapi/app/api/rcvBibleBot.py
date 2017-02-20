# rcvBibleBot.py

import string
import json
import requests

from app import log
from app.database import redis_db
from app.util.stringUtil import preProcess
from app.util import bible_re
from app.errors import AppError, InvalidParameterError
from app import config

LOG = log.get_logger()

def chatBotResponse(message):
    try:
        db = redis_db.RedisStorageEngine()
        r = db.connection()
    except Exception as ex:
        print ex

    fbid = message['sender']['id']
    recevied_message = message['message']['text']
    query = recevied_message.split(" ")
    book = bible_re.get_book(query[0])
    if  book is not None:
        doc_index = book[1] + query[1]
        if len(r.smembers(doc_index)) == 0:
            result = "Oops, cannot find this verse in the Bible."
        else:
            result = recevied_message + " " + next(iter(r.smembers(doc_index)))
    else:
        result = "Oops, cannot find this verse in the Bible."

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=' + config.FB_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":result}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    print(status.json())
