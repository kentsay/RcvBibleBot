# search.py

import falcon
import string
import json
from app import log
from app.database import redis_db
from app.util.stringUtil import preProcess
from app.util import bible_re
from app.errors import AppError, InvalidParameterError
import requests
from app import config

LOG = log.get_logger()

class BibleResoure(object):

    def __init__(self, db):
        self.db = db

    # This function handles GET reuqests
    def on_get(self, req, resp):
        if req.get_param("hub.verify_token") == config.FB_TOKEN:
            resp.body = req.get_param("hub.challenge")

        resp.status = falcon.HTTP_200  # This is the default status

    # This function handles POST reuqests
    def on_post(self, req, resp):
        raw_json = req.stream.read()
        incoming_message = json.loads(raw_json, encoding='utf-8')
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                if 'message' in message:
                    # Print the message to the terminal
                    print(message)
                    post_facebook_message(message['sender']['id'], message['message']['text'])


def post_facebook_message(fbid, recevied_message):
    try:
        db = redis_db.RedisStorageEngine()
        r = db.connection()
    except Exception as ex:
        print ex

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
