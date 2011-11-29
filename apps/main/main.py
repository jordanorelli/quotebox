#!/usr/bin/env python

from gevent import Greenlet
from brubeck.request_handling import Brubeck
from brubeck.templating import load_jinja2_env
import handlers
import os
import sys

Greenlet.spawn(handlers.PollHandler.loop, delay=5)

config = {
    'mongrel2_pair': ('ipc://run/mongrel2_send', 'ipc://run/mongrel2_recv'),
    'handler_tuples': [
        (r'^/$', handlers.IndexHandler),
        (r'^/poll$', handlers.PollHandler),
    ],
    'template_loader': load_jinja2_env('./templates'),
}

app = Brubeck(**config)
if __name__ == '__main__':
    app.run()
