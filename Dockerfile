ARG CODE_VERSION=20.04

FROM ubuntu:${CODE_VERSION}

LABEL Creator: "Siseco-Web-Application"

RUN apt-get update -y \
	&& apt-get install python3.8-dev -y \
	&& apt-get install g++ -y \
	&& apt-get install unixodbc-dev -y \
	&& apt-get install python3-pip -y


ENV USER admin
ENV SHELL /bin/bash
ENV LOGNAME ICMS-admin

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

EXPOSE 5000