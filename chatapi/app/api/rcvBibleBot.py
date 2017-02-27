# rcvBibleBot.py

import string
import json
import requests
from pymongo import MongoClient

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

    if checkFbUser(fbid):
        result = "Hi, welcome to use Recovery version Bible Chat Bot! "\
        "I support only book names, chapters, and verses found in the Recovery Version of the Holy Bible."\
        "You can find the versers by default input mode as Prov. 29:18; Acts 26:19; Eph. 4:4-6; Rev. 21:2, 9-10. "\
        "Anytime you need help, just type help!"\
        "Last by not least, Living Stream Ministry retains full copyright on all these materials and hopes that our visitors will respect this."
    else:
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
    client = MongoClient()
    db = client.rcvbot
    results = db.rcvbot.find({"fbid": fbid}).count()
    if results == 0:
        # It's the first time for this user chat with the bot
        user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
        user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':config.FB_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        print(user_details)
        db.rcvbot.insert({
                        "fbid": fbid,
                        "first_name": user_details['first_name'],
                        "last_name": user_details['last_name'],
                        "profile_pic": user_details['profile_pic']
                        })
        return True
    else:
        # Not a fish
        return False

def responseFbMessage(fbid, message):
    post_message_url = config.FB_MESSAGE_URL + config.FB_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":message}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    print(status.json())
