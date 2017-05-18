FROM fedora

RUN dnf -y update && dnf -y install tar gzip java java-devel && dnf clean all

ENV MAVEN_VERSION=3.5.0

# Download and install Maven
RUN curl -sSL https://repo1.maven.org/maven2/org/apache/maven/apache-maven/$MAVEN_VERSION/apache-maven-$MAVEN_VERSION-bin.tar.gz \
    | tar xzf - -C /usr/share \
    && mv /usr/share/apache-maven-$MAVEN_VERSION /usr/share/maven \
    && ln -s /usr/share/maven/bin/mvn /usr/bin/mvn

ADD pom.xml /pom.xml
ADD src /src

RUN mvn -q -e clean compile -DskipTests

ENTRYPOINT ["mvn", "-q", "-e", "exec:java", "-Dexec.mainClass=com.redhat.example.ImageAnalyzer"]
