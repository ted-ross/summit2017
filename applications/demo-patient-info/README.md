# Patient Information

## Example

    [jross@localhost demo-patient-info (master)]$ make test
    sudo docker build -t test .
    Sending build context to Docker daemon 10.75 kB
    Step 1 : FROM fedora
     ---> 15895ef0b3b2
    Step 2 : MAINTAINER Justin Ross <jross@apache.org>
     ---> Using cache
     ---> e33f00a31e8c
    Step 3 : RUN dnf -y update && dnf -y install npm && dnf clean all
     ---> Using cache
     ---> bf136bdf0c32
    Step 4 : ADD package.json /package.json
     ---> Using cache
     ---> b10dba73e628
    Step 5 : RUN npm install
     ---> Using cache
     ---> a61980ff1483
    Step 6 : ENV MESSAGING_SERVICE_HOST 127.0.0.1
     ---> Using cache
     ---> 72aae8236fce
    Step 7 : ADD main.js /main.js
     ---> 5d997ed2f7dd
    Removing intermediate container 35f78ceee94b
    Step 8 : CMD node main.js
     ---> Running in 30922578c077
     ---> 2d84e84de5aa
    Removing intermediate container 30922578c077
    Successfully built 2d84e84de5aa
    sudo docker run -e MESSAGING_SERVICE_HOST=192.168.86.21 test
    patient-info: Created receiver for source address 'patient-info'
    patient-info: Received request: test
    patient-info: Received request: test
