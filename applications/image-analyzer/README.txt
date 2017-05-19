==========================
Vert.x based ImageAnalyzer
==========================

Either:

# Run the script to build and run:
./image-analyzer

or

# Build and execute manually:

Use maven to build the module, and additionally copy the dependencies alongside their output:

  mvn clean package dependency:copy-dependencies -DincludeScope=runtime -DskipTests

Now you can run it using commands of the format:

  Linux:   java -cp "target/classes/:target/dependency/*" com.redhat.example.ImageAnalyzer

  Windows: java -cp "target\classes\;target\dependency\*" com.redhat.example.ImageAnalyzer

or

# Use Docker:

  sudo docker build -t <some-tag> .
  sudo docker run -e MESSAGING_SERVICE_HOST=<message-server> <some-tag>
