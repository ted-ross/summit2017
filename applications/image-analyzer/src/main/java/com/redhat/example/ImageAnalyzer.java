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
import io.vertx.proton.ProtonSender;

import org.apache.qpid.proton.amqp.messaging.AmqpValue;
import org.apache.qpid.proton.message.Message;

public class ImageAnalyzer {

  private static final String SERVER_HOST = System.getenv("MESSAGING_SERVICE_HOST") != null ? System.getenv("MESSAGING_SERVICE_HOST") : "localhost";
  private static final int SERVER_PORT = 5672;
  private static final String REQUEST_ADDRESS = "image-analyzer";

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

      ProtonSender sender = connection.createSender(null);
      sender.openHandler(x -> {
        connection.createReceiver(REQUEST_ADDRESS).handler((delivery, requestMsg) -> {
          // Process the request and send a response
          String content = getRequestContent(requestMsg);
          System.out.println("image-analyzer: Received request: " + content);

          String response = content + "\nCompleted Image Analysis";

          Message responseMessage = createResponseMessage(requestMsg, response);

          sender.send(responseMessage);
        }).open();
      }).open();
    });
  }

  private static String getRequestContent(Message requestMessage) {
    return (String) ((AmqpValue) requestMessage.getBody()).getValue();
  }

  public static Message createResponseMessage(Message requestMessage, String responseContent) {
    Message responseMessage = Message.Factory.create();
    responseMessage.setAddress(requestMessage.getReplyTo());
    responseMessage.setBody(new AmqpValue(responseContent));
    responseMessage.setCorrelationId(requestMessage.getCorrelationId());
    return responseMessage;
  }
}
