#!/usr/bin/env python

import os
import sys
from brubeck.request_handling import Brubeck, WebMessageHandler

html_body = '''<html>
  <head>
    <title>Brubeck</title>
    <link rel=stylesheet type="text/css" href="static/css/style.css" />
  </head>
  <body>
  <h1>Welcome to Brubeck!</h1>
  <p>Brubeck is blah blah blah blah.</p>
  </body>
</head>
'''

class DemoHandler(WebMessageHandler):
    def get(self):
        self.set_body(html_body)
        return self.render()

config = {
    'mongrel2_pair': ('ipc://run/mongrel2_send', 'ipc://run/mongrel2_recv'),
    'handler_tuples': [
        (r'^/$', DemoHandler),
    ],
}

app = Brubeck(**config)
if __name__ == '__main__':
    app.run()
