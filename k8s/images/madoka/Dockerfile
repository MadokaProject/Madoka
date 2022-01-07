FROM centos:8

LABEL org.opencontainers.image.authors="todest"

RUN yum -y update && \
    yum install -y git python38 python38-pip

WORKDIR /app

CMD ["/bin/bash", "-c", "python3 main.py"]
