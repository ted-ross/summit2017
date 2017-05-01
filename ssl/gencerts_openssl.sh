#!/bin/bash -ex

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
#

# Creates a root CA and intermediate CA and creates password protected server and client certificates using openssl commands

##### Create root CA #####
# Create a password protected private key for root CA
openssl genrsa -aes256 -passout pass:ca-226774 -out ca-private-key.pem 4096

# Use the private key to create a root CA cert
openssl req -key ca-private-key.pem -new -x509 -days 99999 -sha256 -out ca-certificate.pem -passin pass:ca-226774 -subj "/C=US/ST=MA/L=Westford/O=Red Hat Inc./CN=QDRCA.demo.redhat.com"



##### Create the enterprise certificate signed by the root CA #####
# Create a password protected client private key which will be used to create the client certificate
mkdir -p enterprise
openssl genrsa -aes256 -passout pass:cert-226774 -out enterprise/private-key.pem 4096

# Create a CSR using the client private key created from the previous step
openssl req -new -key enterprise/private-key.pem -passin pass:cert-226774 -out enterprise.csr -subj "/C=US/ST=MA/L=Westford/O=Enterprise/CN=enterprise.demo.redhat.com"

# Now the CSR has been created and must be sent to the CA.
# The root CA receives the CSR and runs this command to create a client certificate (client_certificate.pem)
openssl x509 -req -in enterprise.csr -CA ca-certificate.pem -CAkey ca-private-key.pem -CAcreateserial -days 9999 -out enterprise/certificate.pem -passin pass:ca-226774


##### Create the aws certificate signed by the root CA #####
mkdir -p aws
openssl genrsa -aes256 -passout pass:cert-226774 -out aws/private-key.pem 4096
openssl req -new -key aws/private-key.pem -passin pass:cert-226774 -out aws.csr -subj "/C=US/ST=MA/L=Westford/O=AWS/CN=aws.demo.redhat.com"
openssl x509 -req -in aws.csr -CA ca-certificate.pem -CAkey ca-private-key.pem -CAcreateserial -days 9999 -out aws/certificate.pem -passin pass:ca-226774

##### Create the azure certificate signed by the root CA #####
mkdir -p azure
openssl genrsa -aes256 -passout pass:cert-226774 -out azure/private-key.pem 4096
openssl req -new -key azure/private-key.pem -passin pass:cert-226774 -out azure.csr -subj "/C=US/ST=MA/L=Westford/O=Azure/CN=azure.demo.redhat.com"
openssl x509 -req -in azure.csr -CA ca-certificate.pem -CAkey ca-private-key.pem -CAcreateserial -days 9999 -out azure/certificate.pem -passin pass:ca-226774


# Verify the certs with the cert chain
openssl verify -verbose -CAfile ca-certificate.pem enterprise/certificate.pem
openssl verify -verbose -CAfile ca-certificate.pem aws/certificate.pem
openssl verify -verbose -CAfile ca-certificate.pem azure/certificate.pem
