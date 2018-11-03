FROM debian:stretch-slim

RUN apt-get update && apt-get install -y python3 && apt-get clean

WORKDIR /src

ADD . /src

CMD python3 ./main.py