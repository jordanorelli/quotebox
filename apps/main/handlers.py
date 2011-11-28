from brubeck.request_handling import JSONMessageHandler
from brubeck.templating import Jinja2Rendering
from gevent import sleep
from gevent.event import Event
from quotes import get_quote
import subprocess

class IndexHandler(Jinja2Rendering):
    def get(self):
        return self.render_template('index.html', quote=get_quote())


class PollHandler(JSONMessageHandler):
    quote_timer = Event()

    @classmethod
    def loop(cls):
        while True:
            cls.quote = subprocess.check_output("fortune", shell=True)
            cls.quote_timer.set()
            cls.quote_timer.clear()
            cls.quote_timer.wait(3)

    def get(self):
        self.quote_timer.wait()
        self.set_status(200)
        self.add_to_payload('quote', self.__class__.quote)
        return self.render()
