# author: oskar.blom@gmail.com
#
# Make sure your gevent version is >= 1.0
import gevent
#from gevent.wsgi import WSGIServer
#from gevent.queue import Queue
import eventlet
from eventlet import wsgi
from flask import Flask, Response

import json
# SSE "protocol" is described here: http://mzl.la/UPFyxY
class ServerSentEvent(object):

    def __init__(self, eventName, data):
        self.data = data
        self.event = eventName
        self.id = None
        self.desc_map = {
            self.data : "data",
            self.event : "event",
            self.id : "id"
        }

    def encode(self):
        if not self.data:
            return ""
        lines = ["%s: %s" % (v, k)
                 for k, v in self.desc_map.iteritems() if k]

        return "%s\n\n" % "\n".join(lines)


subscriptions = []

def debug():
    return "Currently %d subscriptions" % len(subscriptions)

def sse_publish(event, message):
    def notify():
        print 'notifying'
        msg = json.dumps(message)
        for sub in subscriptions[:]:
            sub.put((event, msg))  # tuple containing event name and serialised data
    eventlet.spawn(notify)
    #notify()
    # return "OK"


def sse_subscribe():
    def gen():
        q = eventlet.queue.Queue()
        subscriptions.append(q)
        try:
            while True:
                event = q.get()
                ev = ServerSentEvent(event[0], event[1])
                yield ev.encode()
        except GeneratorExit:
            subscriptions.remove(q)
    return Response(gen(), mimetype="text/event-stream")

    # Then visit http://localhost:5000 to subscribe
    # and send messages by visiting http://localhost:5000/publish
