# Patient Information

## Example

    [jross@localhost demo-patient-info (master)]$ make test TEST_SERVICE=192.168.86.21
    if [[ 192.168.86.21 == "" ]]; then echo TEST_SERVICE is not set; exit 1; fi;
    sudo docker build -t test .
    Sending build context to Docker daemon 8.704 kB
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
    Step 5 : ADD main.js /main.js
     ---> Using cache
     ---> 7cb91bcedb07
    Step 6 : RUN npm install
     ---> Using cache
     ---> 3084c62bc56b
    Step 7 : ENTRYPOINT node main.js
     ---> Using cache
     ---> 348075aef814
    Successfully built 348075aef814
    sudo docker run -e MESSAGING_SERVICE_HOST=192.168.86.21 test
    patient-info: Created receiver for source address 'patient-info'
