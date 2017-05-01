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

class Service(MessagingHandler):
    def __init__(self, url):
        super(Service, self).__init__()
        self.url = url
        self.address = "SubService.B"

    def on_start(self, event):
        self.container   = event.container
        self.conn        = self.container.connect(self.url)
        self.receiver    = self.container.create_receiver(self.conn, self.address)
        self.anon_sender = self.container.create_sender(self.conn, None)

    def on_message(self, event):
        reply_to = event.message.reply_to
        cid      = event.message.correlation_id
        msg = Message(address = reply_to, correlation_id = cid, body = "SubService.B (%s)" % os.uname()[1])
        self.anon_sender.send(msg)

try:
    ##
    ## Try to get the message bus hostname from the openshift environment
    ## Fall back to 127.0.0.1 (loopback)
    ##
    host = os.getenv("MESSAGING_SERVICE_HOST", "127.0.0.1")
    Container(Service(host)).run()
except KeyboardInterrupt: pass



