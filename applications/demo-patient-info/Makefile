TEST_SERVICE := ""

.PHONY:
test:
	if [[ ${TEST_SERVICE} == "" ]]; then echo TEST_SERVICE is not set; exit 1; fi;
	sudo docker build -t test .
	sudo docker run -e MESSAGING_SERVICE_HOST=${TEST_SERVICE} test
