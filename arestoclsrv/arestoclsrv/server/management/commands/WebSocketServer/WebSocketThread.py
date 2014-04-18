#!/usr/bin/env python

import threading
import tornado.httpserver
import tornado.ioloop
import tornado.web

from WebSocketClient import WebSocketClient


class WebSocketThread(threading.Thread):
    """
    This class is used for multithreading. WebSocketThread contain a tornado server.
    """
    def __init__(self, path, port):
        """
        init methodn init wsPath, wsPort and thread.
        """
        threading.Thread.__init__(self)
        self.wsPath = path
        self.wsPort = port

    def run(self):
        """
        Lunch a instance of tornado.
        """
        application = tornado.web.Application([
                (r'%s' % self.wsPath, WebSocketClient),
                ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(self.wsPort)
        tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    webSocketServerTest = WebSocketThread('/ws', 8888)
    webSocketServerTest.start()
    print "< Start websocket...."
