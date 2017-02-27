# rcvBibleBot.py

import string
import json
import requests

from app import log
from app.database import redis_db
from app.util.stringUtil import preProcess
from app.util import bible_re
from app.util import fbUtil
from app.errors import AppError, InvalidParameterError
from app import config

LOG = log.get_logger()

def chatBotResponse(message):
    try:
        db = redis_db.RedisStorageEngine()
        r = db.connection()
    except Exception as ex:
        print ex

    fbid = fbUtil.getFbId(message)
    recevied_message = fbUtil.getFbMessage(message)

    checkFbUser(fbid)
    query = recevied_message.split(" ")
    book = bible_re.get_book(query[0])
    if  book is not None:
        doc_index = book[1] + query[1]
        if len(r.smembers(doc_index)) == 0:
            result = "Oops, cannot find this verse in the Bible."
        else:
            ## check if it's a single verse or a range
            result = recevied_message + " " + next(iter(r.smembers(doc_index)))
    else:
        result = "Oops, cannot find this verse in the Bible."

    responseFbMessage(fbid, result)

def checkFbUser(fbid):
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':config.FB_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    print(user_details)

def responseFbMessage(fbid, message):
    post_message_url = config.FB_MESSAGE_URL + config.FB_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    print(status.json())
