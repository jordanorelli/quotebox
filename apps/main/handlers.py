from brubeck.request_handling import JSONMessageHandler
from brubeck.templating import Jinja2Rendering
from gevent.event import Event
from quotes import get_quote
import subprocess

class IndexHandler(Jinja2Rendering):
    """Renders the main HTML document based on the Jinja2 template 'index.html'
    """

    def get(self):
        """Brubeck will automatically route an HTTP GET request here."""
        return self.render_template('index.html', quote=PollHandler.quote)


class PollHandler(JSONMessageHandler):
    """Handles our long polling clients."""
    quote_timer = Event()

    @classmethod
    def loop(cls, delay):
        """Loops infinitely."""
        while True:
            cls.quote = subprocess.check_output("fortune", shell=True)
            cls.quote_timer.set()
            cls.quote_timer.clear()
            cls.quote_timer.wait(delay)

    def get(self):
        self.quote_timer.wait()
        self.set_status(200)
        self.add_to_payload('quote', self.quote)
        return self.render()
