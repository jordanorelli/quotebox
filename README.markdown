Quotebox is a demo project for [Brubeck](http://brubeck.io/), an asyncronous
Python web application framework.  I use this project as a personal reference
project.  It demonstrates uses of Brubeck's template support, as well as one
strategy for implementing a
[Comet](http://en.wikipedia.org/wiki/Comet_\(programming\)) service (i.e.,
*long polling*) with [gevent](http://www.gevent.org/).  Specifically, Quotebox
puts all clients on a single timed loop; in this way, all clients are updated
simultaneously and clients are (roughly) syncronized.  This is made very
obvious if you run the application and view it in multiple browser windows.
Quotebox simply turns http requests into shell calls to
[fortune](http://en.wikipedia.org/wiki/Fortune_\(Unix\)).  Generally it's a
terrible idea to route http requests to shell calls, but I figure it's more
sensible than coming up with a big quote database myself; you can easily
substitute the call to `fortune` for a different quote-generating strategy.
`fortune` can be easily obtained from your OS's package manager, e.g.
[apt](http://en.wikipedia.org/wiki/Advanced_Packaging_Tool),
[yum](http://en.wikipedia.org/wiki/Yellowdog_Updater,_Modified), or
[homebrew](http://mxcl.github.com/homebrew/) if you're on OS X.

## How It Works

Brubeck sits behind [Mongrel2](http://mongrel2.org/), the language-agnostic
HTTP server by [Zed Shaw](https://github.com/zedshaw).  Mongrel2 takes HTTP
requests and passes them along to Brubeck via [ZeroMQ](http://www.zeromq.org/).
The actual routes that define which URLs will be served by Mongrel2 directly,
in contrast with those that are
[proxied](http://en.wikipedia.org/wiki/Reverse_proxy) to Brubeck, are defined
in `conf/mongrel2.conf`.  Routing is continued at the application level.
Brubeck internally routes each request to a specific code entry point, which in
Brubeck is called a *handler*.  Brubeck's application-level routes are
configured in `apps/main/main.py`.  For this application there are only two
routes: `/` and `/poll`, which point to the `IndexHandler` and `PollHandler`
classes, respectively.  The handler classes themselves are defined in
`apps/main/handlers.py`.

### The `IndexHandler` handler

`IndexHandler` is a pretty standard handler.  All it does is render a
[Jinja2](http://jinja.pocoo.org/docs/) template to HTML and return it to the
user.  It also fills in the current quote, so that when a user first hits the
page they see the same quote that everyone else is currently looking at.  Like
the routes, the template engine is initialized in `apps/main/main.py`.  (if
you're reading the source along with the README, the quote rotation will be
explained in a bit.)

The template that we're interested in is found in `templates/index.html`.  It
illustrates some features of the Jinja2 templating engine, namely template
inheritance and how to use Jinja2's block system.  If you are familiar with
Django templates, Jinja2 templates should look very familiar.  The only
differences in this example are that Jinja2 says `{{ super() }}` instead of
Django's `{{ block.super }}`, and Jinja2 allows you to clear the whitespace
before and after a template tag using the `{%-` and `-%}` opening and closing
tags, respectively.  There are more difference between the template engines,
but they're not illustrated here.

### The `PollHandler` handler

`PollHandler` is a bit different.  Unlike most Brubeck handlers (or Django
views, or Rails controllers), `PollHandler` does not simply respond to each
request as fast as possible.  Instead, it holds onto the request in memory and
halts execution.  This is accomplished using a gevent
[Event](http://www.gevent.org/gevent.event.html#gevent.event.Event) object (yes
the class is really called `gevent.event.Event`).  The Event instance is stored
at the class level.  Within the `PollHandler.get` method, the call to
`self.quote_timer.wait()` causes the execution of the current HTTP request to
freeze until the `PollHandler` class's `quote_timer` Event instance is
awakened, using the
[`Event.set`](http://www.gevent.org/gevent.event.html#gevent.event.Event.set)
method.  When this occurs, the processing of the current HTTP request
continues; the HTTP status code is set to 200 (success) and the quote itself is
read from the `PollHandler` class's `quote` attribute (so that everyone is
looking at the same quote) and added to the response body using the
`add_to_payload` method.  This method is available on `PollHandler` because it
is defined by Brubeck's `JSONMessageHandler` class, which `PollHandler` is
descended from.  The `JSONMessageHandler` class will take care of the rest for
us, including composing the rest of the HTTP response and setting the response
`content-type` header to `application/json`.

So, the last remaining piece of the puzzle on the server is the rotation of the
quotes and the unfreezing of incoming poll requests.  When the application is
launched, we kick off the `PollHandler` class's `loop` method, which will loop
indefinitely.  It starts by getting a new quote from `fortune` using Python's
[`subprocess` module](http://docs.python.org/library/subprocess.html).  Now
that it has a new quote, it wakes up all active poll requests:
`cls.quote_timer.set()`.  It then sets the Event's internal flag to false with
`cls.quote_timer.clear()`, which will cause future poll requests to be halted.
We then use the Event's `wait` method to halt execution of the
`PollHandler.loop` method for some fixed amount of time.

### The jQuery client

Finally, the client is a fairly straightforward AJAX script written with
jQuery.  The client simply sends HTTP GET requests to `/poll`, fades out the
old quote, swaps it with the new quote, and fades it back in.  The AJAX call
itself recurses indefinitely, as defined in the `poll` method's `complete`
callback.  The client sends its first request on page load.  Every time a
request times out or is answered, we instantly send a new request, since it's
assumed that it will be queued on the server.

For installation notes, please refer to the [Brubeck Installation
Instructions](http://brubeck.io/installing.html), which are quite complete.  If
you have trouble installing, please drop me a line here on GitHub or send an
email to jordan@prehype.com and I'll be happy to help you get the project
running.

note: browsers have a limit on the number of outstanding http requests they can
send to a single domain before the browser starts queuing the requests,
typically between two and six, but it varies between browser and between
version.  Chrome 15 on OS X, for example, tops out at six.  As a result, the
effective number of browser windows you can sync on a single machine is
limited, but you can use multiple browsers or multiple machines to see the sync
happen in greater numbers.
