FROM openjdk:11-jre

LABEL org.opencontainers.image.authors="todest"

ENV TZ Asia/Shanghai
WORKDIR /app
ADD ./mcl/ .

RUN chmod +x mcl

ENTRYPOINT ["./mcl"]
