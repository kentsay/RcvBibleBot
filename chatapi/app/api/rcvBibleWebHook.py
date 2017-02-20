# rcvBibleWebHook.py

import falcon
import json
from rq import Queue
from rq.job import Job

from app import log
from app import config
from app.database import redis_db
from rcvBibleBot import chatBotResponse

LOG = log.get_logger()

class BibleResoure(object):

    def __init__(self, db):
        self.db = db

    # This function handles GET reuqests
    def on_get(self, req, resp):
        # FB Messenger WebHook token verify
        if req.get_param("hub.verify_token") == config.FB_TOKEN:
            resp.body = req.get_param("hub.challenge")
        else:
            LOG.error('verify_token is not correct')
        resp.status = falcon.HTTP_200

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
                    """
                    Enqueueing each message as jobs into fb_message queue
                    and processing them in the background with workers.
                    """
                    q = Queue('fb_message', connection=self.db.connection())
                    job = q.enqueue_call(
                        func=chatBotResponse, args=(message,), result_ttl=5000
                    )
                    LOG.info('fb_message: ' + message)
                    #post_facebook_message(message['sender']['id'], message['message']['text'])
