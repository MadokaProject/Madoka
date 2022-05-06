FROM python:3.8-slim

LABEL org.opencontainers.image.authors="colsrch"

ENV TZ Asia/Shanghai
ENV LANG C.UTF-8

WORKDIR /app

COPY Madoka .

RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "python main.py"]