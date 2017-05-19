#!/usr/bin/env python
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#

from __future__ import print_function, unicode_literals
import optparse
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container, DynamicNodeProperties
import os

class Timer(object):
    def __init__(self, parent):
        self.parent = parent

    def on_timer_task(self, event):
        self.parent.tick()


class Client(MessagingHandler):
    def __init__(self, url, rate):
        super(Client, self).__init__()
        self.url = url
        self.rate = rate
        self.sender = None
        self.sent = 0
        self.send_count = self.rate / 2

    def send(self):
        if self.sender == None:
            return

        to_send = self.send_count
        if self.sender.credit < self.send_count:
            to_send = self.sender.credit
        self.send_count -= to_send
        for i in range(to_send):
            msg = Message(reply_to = self.reply_to, correlation_id = 0, body = "Physician Request")
            self.sender.send(msg)
            self.sent += 1

    def tick(self):
        self.timer = self.reactor.schedule(0.5, Timer(self))
        self.send_count = self.rate / 2
        self.send()

    def on_start(self, event):
        self.container = event.container
        self.reactor   = event.reactor
        self.conn      = event.container.connect(self.url)
        self.receiver  = event.container.create_receiver(self.conn, None, dynamic=True)
        self.timer     = self.reactor.schedule(0.5, Timer(self))

    def on_link_opened(self, event):
        if event.receiver == self.receiver:
            self.reply_to = event.receiver.remote_source.address
            self.sender   = event.container.create_sender(self.conn, "procedure-recommend")

    def on_sendable(self, event):
        self.send()

    def on_message(self, event):
        print("%s" % event.message.body)


try:
    ##
    ## Try to get the message bus hostname from the openshift environment
    ## Fall back to 127.0.0.1 (loopback)
    ##
    host = os.getenv("MESSAGING_SERVICE_HOST", "127.0.0.1")
    Container(Client(host, 10)).run()
except KeyboardInterrupt: pass
