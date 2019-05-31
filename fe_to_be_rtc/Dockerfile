FROM node:8
LABEL maintainer chris
RUN mkdir /docker_api
WORKDIR /docker_api

ADD . /docker_api

RUN npm install 

RUN chmod u+x docker-entrypoint.sh
ENTRYPOINT ["/bin/bash", "docker-entrypoint.sh"]