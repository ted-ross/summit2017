FROM fedora

RUN dnf -y update && dnf -y install npm && dnf clean all

ADD package.json /package.json
ADD main.js /main.js

RUN npm install

ENTRYPOINT ["node", "main.js"]
