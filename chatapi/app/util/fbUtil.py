#fbUtil.py

def getFbId(message):
    if message is not None:
        fbid = message['sender']['id']
        return fbid
    else:
        return -1

def getFbMessage(message):
    if message is not None:
        recevied_message = message['message']['text']
        return recevied_message
    else:
        return None
