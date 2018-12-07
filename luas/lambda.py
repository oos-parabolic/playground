import logging
from flask import Flask
from flask_ask import Ask, statement
import api
import models

app = Flask(__name__)
ask = Ask(app, '/')
logger = logging.getLogger()

@ask.launch
def launch():
    return stats()

@ask.intent("StatsIntent")
def stats():
    a = api.LuasClient()
    in_time = a.next_tram('STI', models.LuasDirection.Inbound).due
    out_time = a.next_tram('STI', models.LuasDirection.Outbound).due
    speech = f"{in_time} from town and {out_time} out of town. that will be 500 euro please "
    logger.info('speech = {}'.format(speech))
    return statement(speech)



