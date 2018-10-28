#!/bin/sh
# Generate self-signed SSL
cd private
openssl req -newkey rsa:2048 -nodes -keyout private.key -x509 -days 365 -out cert.pem -subj '/CN=localhost'