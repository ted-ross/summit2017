FROM fedora
MAINTAINER Justin Ross <jross@apache.org>

RUN dnf -y update && dnf -y install npm && dnf clean all

ADD package.json /package.json
ADD main.js /main.js

RUN npm install

ENV MESSAGING_SERVICE_HOST=127.0.0.1

ENTRYPOINT ["node", "main.js"]
