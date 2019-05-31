FROM ubuntu:18.04
FROM python:3.6.5
MAINTAINER chris
ENV DEBIAN_FRONTEND nonineractive
RUN apt update && apt upgrade -y

RUN apt install python3 -y
RUN apt install python3-pip -y
RUN apt install python3-dev -y
RUN python3 -V
RUN pip3 -V
RUN pip3 install --upgrade pip
RUN pip -V


RUN apt install libopus-dev -y
RUN apt install libvpx-dev -y
RUN apt install libffi-dev -y
RUN apt install libssl-dev -y
RUN apt install libopencv-dev -y

RUN apt-get install -y python-dev pkg-config
RUN apt-get install -y libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev

RUN mkdir /docker_api
WORKDIR /docker_api
ADD . /docker_api
RUN pip install -i https://pypi.douban.com/simple --upgrade pip
RUN pip install -r requirements.txt

RUN chmod u+x docker-entrypoint.sh
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]
