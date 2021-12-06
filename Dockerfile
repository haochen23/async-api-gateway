FROM ubuntu:20.04

LABEL MAINTAINER  "Eric Chen"

ARG HTTP_PROXY
ARG HTTPS_PROXY

ENV HTTP_PROXY=$HTTP_PROXY
ENV HTTPS_PROXY=$HTTPS_PROXY
ENV https_proxy=$HTTPS_PROXY
ENV http_proxy=$HTTP_PROXY
ENV no_proxy="localhost,127.0.0.0/8,::1,atcvt,`echo 172.19.0.{1..255} | sed 's/ /,/g'`"
ENV NO_PROXY=$no_proxy
ENV TIMEZONE=Pacific/Auckland
RUN ln -snf /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && echo ${TIMEZONE} > /etc/timezone
RUN apt-get update && apt-get install -y python3 python3-setuptools python3-pip iputils-ping dnsutils curl

WORKDIR /repo
COPY . /repo

RUN pip3 install -r requirements.txt

CMD hypercorn app:app

EXPOSE 9000
