from twisted.internet import protocol
from twisted.web import server, resource, http

# from http://nullege.com/codes/show/src%40p%40l%40planes-HEAD%40twisted_serve.py/6/twisted.web.http.HTTPChannel/python
class MyHttpRequest(http.Request):
  
    def process(self):
        if self.method == "POST":
	    print "POST from %s to %s: %s" % (self.getClientIP(), self.uri, self.args)
        # self.responseHeaders type is http_headers.Headers
        self.setHeader("Server", "%s v%s (%s)" % (self.channel.factory.APP_NAME, self.channel.factory.APP_VERSION, self.channel.factory.APP_URL))
        # self.getHeader(key) returns bytes or NoneType
        # self.getAllHeaders() - returns a dict of all response headers
        if self.path == "/notification/send":
            if self.channel.factory.VERBOSE:
                print "MyHttpRequest.process() self.args: %s" % self.args
            channels = None
            users = None
            if "channels" in self.args:
                channels = self.args['channels']
            if "users" in self.args:
                users = self.args['users']
            if "message" in self.args:
                self.channel.factory.message(self.args['message'][0], channels, users)
                self.setResponseCode(202, message="Message passed to notifiers.")
                self.write("message passed to notifiers")
            else:
                self.setResponseCode(400, message="message not specified")
        else:
            self.setResponseCode(404, message="invalid path")
        self.finish() # this also writes out an access log line

class Channel(http.HTTPChannel):
    requestFactory = MyHttpRequest
    

class HTTPServerFactory(http.HTTPFactory):

    protocol = Channel
    _logDateTimeCall = None

    def __init__(self, config, APP_VERSION, APP_NAME, APP_URL, VERBOSE, **kwargs):
        self.config = config
        self.APP_VERSION = APP_VERSION
        self.APP_NAME = APP_NAME
        self.APP_URL = APP_URL
        self.VERBOSE = VERBOSE
        self.connections = kwargs['factories']

    def message(self, message, channels = None, users = None):
	for connection in self.connections:
            if self.VERBOSE:
                print "HTTPServerFactory.message(%s, %s, %s)" % (message, channels, users)
            connection.msg(message, channels, users)
