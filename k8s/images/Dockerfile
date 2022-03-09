FROM rockylinux:8.5

LABEL org.opencontainers.image.authors="colsrch"

WORKDIR /app
COPY Madoka ./

ENV TZ Asia/Shanghai
ENV LANG C.UTF-8

RUN yum install -y git python38 python38-pip wget && \
    pip3 install -r requirements.txt

CMD ["/bin/bash", "-c", "python3 main.py"]