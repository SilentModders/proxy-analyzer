#!/bin/sh
# Generate self-signed SSL

PRIVATE_DIR="private"
HOSTNAME="localhost"
CERTNAME="${1:-server}"

cd "$PRIVATE_DIR" && \
openssl req -newkey rsa -nodes -keyout "$CERTNAME.key" -x509 -days 365 -out "$CERTNAME.pem" -subj "/CN=$HOSTNAME"
openssl dhparam -out dhparams.pem 2048
