/*
* Copyright 2017 the original author or authors.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
* http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/
package com.redhat.example;

import io.vertx.core.Vertx;
import io.vertx.proton.ProtonClient;
import io.vertx.proton.ProtonConnection;
import io.vertx.proton.ProtonDelivery;
import io.vertx.proton.ProtonSender;

import java.util.LinkedList;
import java.util.Queue;

import org.apache.qpid.proton.amqp.messaging.Accepted;
import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.message.Message;

public class ImageAnalyzer2 {

  private static final String SERVER_HOST = System.getenv("MESSAGING_SERVICE_HOST") != null ? System.getenv("MESSAGING_SERVICE_HOST") : "localhost";
  private static final int SERVER_PORT = 5672;
  private static final String REQUEST_ADDRESS = "queue";

  public static void main(String[] args) {
    Vertx vertx = Vertx.vertx();

    ProtonClient client = ProtonClient.create(vertx);

    client.connect(SERVER_HOST, SERVER_PORT, res -> {
      if (!res.succeeded()) {
        System.out.println("Failed to connect: " + res.cause());
        vertx.close();
        return;
      }

      ProtonConnection connection = res.result();
      connection.open();

      Queue<Request> outstandingRequests = new LinkedList<>();

      ProtonSender sender = connection.createSender(null);
      sender.openHandler(x -> {
        connection.createReceiver(REQUEST_ADDRESS).setAutoAccept(false).handler((delivery, requestMsg) -> {
          // Queue the request for later completion
          Request request = new Request(delivery, requestMsg);
          outstandingRequests.add(request);

          System.out.println("Received request: " + request.content);
        }).open();
      }).open();

      // Periodically process an outstanding request and send a response
      vertx.setPeriodic(1000, timerId -> {
        Request req = outstandingRequests.poll();
        if(req != null) {
          String response = req.content + "\nCompleted Image Analysis";
          Message responseMessage = createResponseMessage(req, response);

          sender.send(responseMessage);

          req.delivery.disposition(Accepted.getInstance(), true);
        }
      });
    });
  }

  private static class Request {
    ProtonDelivery delivery;
    String content;
    String responseAddress;
    Object correlationId;

    public Request(ProtonDelivery delivery, Message requestMessage) {
      this.delivery = delivery;
      this.responseAddress = requestMessage.getReplyTo();
      this.content = getRequestContent(requestMessage);
      this.correlationId = requestMessage.getCorrelationId();
    }
  }

  private static String getRequestContent(Message requestMessage) {
    return (String) ((AmqpValue) requestMessage.getBody()).getValue();
  }

  private static Message createResponseMessage(Request req, String response) {
    Message responseMessage = Message.Factory.create();
    responseMessage.setAddress(req.responseAddress);
    responseMessage.setBody(new AmqpValue(response));
    responseMessage.setCorrelationId(req.correlationId);

    return responseMessage;
  }

}
