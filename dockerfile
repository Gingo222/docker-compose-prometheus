FROM python:3.7.1 as build

MAINTAINER shukunqa

CMD mkdir /opt/shukunqa-sys-alert
WORKDIR /opt/shukunqa-sys-alert
ADD . /opt/shukunqa-sys-alert

RUN pip install -r requirements.txt

