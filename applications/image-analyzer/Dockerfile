FROM fedora

RUN dnf -y update && dnf -y install maven && dnf clean all

ADD pom.xml /pom.xml
ADD src /src

RUN mvn -q -e clean compile -DskipTests

ENTRYPOINT ["mvn", "-q", "-e", "exec:java", "-Dexec.mainClass=com.redhat.example.ImageAnalyzer"]
