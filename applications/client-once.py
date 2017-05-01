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

class Client(MessagingHandler):
    def __init__(self, url):
        super(Client, self).__init__()
        self.url = url
        self.sent = False

    def on_start(self, event):
        self.conn     = event.container.connect(self.url)
        self.receiver = event.container.create_receiver(self.conn, None, dynamic=True)

    def on_link_opened(self, event):
        if event.receiver == self.receiver:
            self.reply_to = event.receiver.remote_source.address
            self.sender   = event.container.create_sender(self.conn, "Service")

    def on_sendable(self, event):
        if not self.sent:
            msg = Message(reply_to = self.reply_to, correlation_id = 0, body = "Client Request")
            self.sender.send(msg)
            self.sent = True

    def on_message(self, event):
        print("%s" % event.message.body)

    def on_settled(self, event):
        self.conn.close()

Container(Client("amq02.lab.eng.rdu2.redhat.com")).run()

