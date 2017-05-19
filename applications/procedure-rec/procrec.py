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

from __future__ import print_function
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container, DynamicNodeProperties
from time import time
import os

REQUEST_STATE_WAIT_A = 1
REQUEST_STATE_WAIT_B = 2
MAX_AGE              = 10.0

class Timer(object):
    def __init__(self, parent):
        self.parent = parent

    def on_timer_task(self, event):
        self.parent.tick()


class Request(object):
    def __init__(self, parent, delivery, message):
        self.parent   = parent
        self.delivery = delivery
        self.body     = message.body + "\nProcessing request from Physician App (%s)" % os.uname()[1]
        self.start    = time()
        self.cid      = message.correlation_id
        self.reply_to = message.reply_to
        self.state    = REQUEST_STATE_WAIT_A
        self.parent.send_sub_request('A', self, self.body)

    def on_response(self, message):
        self.body += "\nReceived sub-result: " + message.body
        if self.state == REQUEST_STATE_WAIT_A:
            self.state = REQUEST_STATE_WAIT_B
            self.parent.send_sub_request('B', self, self.body)
        else:
            self.body += "\nCompleted service, sending response (elapsed: %f)" % (time() - self.start)
            self.parent.send_response(self.body, self.reply_to, self.cid)
            self.parent.settle_request(self)


class Service(MessagingHandler):
    def __init__(self, url, rate):
        super(Service, self).__init__(auto_accept = False)
        self.url = url
        self.rate = rate
        self.address = "procedure-recommend"
        self.sub_a_address = "patient-info"
        self.sub_b_address = "image-analyzer"
        self.sequence = 0
        self.sequence_map = {}
        self.to_be_settled = []
        self.can_accept = self.rate / 2  # acceptances per half-second

    def send_sub_request(self, subsrv, request, body):
        sender = self.sub_a_sender
        if subsrv == 'B':
            sender = self.sub_b_sender
        msg = Message(reply_to = self.reply_to, correlation_id = self.sequence, body = body)
        self.sequence_map[self.sequence] = request
        self.sequence += 1
        sender.send(msg)

    def send_response(self, body, reply_to, cid):
        msg = Message(body = body, address = reply_to, correlation_id = cid)
        self.anon_sender.send(msg)

    def settle_request(self, request):
        if self.can_accept > 0:
            self.accept(request.delivery)
            self.can_accept -= 1
        else:
            self.to_be_settled.insert(0, request)

    def tick(self):
        ##
        ## Schedule the next half-second tick
        ##
        self.timer = self.reactor.schedule(0.5, Timer(self))
        self.can_accept = self.rate / 2

        ##
        ## Settle any pending requests
        ##
        while len(self.to_be_settled) > 0 and self.can_accept > 0:
            request = self.to_be_settled.pop()
            self.accept(request.delivery)
            self.can_accept -= 1

        ##
        ## Age out stuck requests
        ##
        seqs = self.sequence_map.keys()
        now  = time()
        for s in seqs:
            if now - self.sequence_map[s].start > MAX_AGE:
                request = self.sequence_map.pop(s)
                self.release(request.delivery)

    def on_start(self, event):
        self.container      = event.container
        self.reactor        = event.reactor
        self.conn           = self.container.connect(self.url)
        self.reply_receiver = self.container.create_receiver(self.conn, None, dynamic=True)
        self.timer          = self.reactor.schedule(0.5, Timer(self))

    def on_link_opened(self, event):
        if event.receiver == self.reply_receiver:
            self.reply_to     = event.receiver.remote_source.address
            self.receiver     = self.container.create_receiver(self.conn, self.address)
            self.sub_a_sender = self.container.create_sender(self.conn, self.sub_a_address)
            self.sub_b_sender = self.container.create_sender(self.conn, self.sub_b_address)
            self.anon_sender  = self.container.create_sender(self.conn, None)

    def on_message(self, event):
        if event.receiver == self.receiver:
            ##
            ## This is a new client request received on the service address
            ##
            request = Request(self, event.delivery, event.message)

        elif event.receiver == self.reply_receiver:
            ##
            ## This is a response to a sub-service request
            ##
            cid = event.message.correlation_id
            if cid in self.sequence_map:
                request = self.sequence_map.pop(cid)
                request.on_response(event.message)
                self.accept(event.delivery)

try:
    ##
    ## Try to get the message bus hostname from the openshift environment
    ## Fall back to 127.0.0.1 (loopback)
    ##
    host = os.getenv("MESSAGING_SERVICE_HOST", "127.0.0.1")
    Container(Service(host, 10)).run()
except KeyboardInterrupt: pass



