import json
import logging
import random
import urllib
import urllib2
from interpreter import Interpreter
import os
# import sys
import pickle
from io import StringIO

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = TELEGRAM_TOKEN

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)

class Game(ndb.Model):
    machine = ndb.PickleProperty()

# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def setGame(chat_id, interpreter):
    game = Game.get_or_insert(str(chat_id))
    game.machine = pickle.dumps(interpreter)
    game.put()

def getGame(chat_id):
    game = Game.get_by_id(str(chat_id))
    if game:
        return pickle.loads(game.machine)
    return None

# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']
        # f = StringIO()
        # f1 = sys.stdin

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            # elif text == '/image':
            #     img = Image.new('RGB', (512, 512))
            #     base = random.randint(0, 16777216)
            #     pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
            #     img.putdata(pixels)
            #     output = StringIO()
            #     img.save(output, 'JPEG')
            #     reply(img=output.getvalue())
            elif text == '/new':
                reply('New game started')
                # sys.stdin = f
                path = os.path.join(os.path.split(__file__)[0], 'hhgg.z3')
                file = open(path, "rb")
                machine = Interpreter(file, '')
                setGame(chat_id, machine)
                try:
                    machine.start(0)
                except KeyboardInterrupt:
                    # sys.stdin = f1
                    reply(machine.o)
                except:
                    # sys.stdin = f1
                    raise Exception
            elif text == '/end':
                setGame(chat_id, {})
                reply("Game ended")
            else:
                reply('What command?')

        # CUSTOMIZE FROM HERE

        else:
            if getEnabled(chat_id):
                machine = getGame(chat_id)
                if machine != None and machine != {}:
                    # sys.stdin = f
                    # f.seek(0)
                    # f.write(text + '\n')
                    # f.seek(0)
                    machine.i = text + '\n'
                    machine.o = ''
                    try:
                        machine.start(0, True)
                    except KeyboardInterrupt:
                        # sys.stdin = f1
                        setGame(chat_id, machine)
                        reply(machine.o)
                    except:
                        # sys.stdin = f1
                        raise Exception
                else:
                    reply(message['from']['first_name'] + ': ' + text)
            else:
                logging.info('not enabled for chat_id {}'.format(str(chat_id)))


app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
