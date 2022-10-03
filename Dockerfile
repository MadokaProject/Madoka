FROM colsrch/pdm:latest AS builder

WORKDIR /build
COPY pdm.lock pyproject.toml ./

RUN pdm config python.use_venv false
RUN pdm install -G mysql --prod --no-lock --no-editable

FROM python:3.9-slim

LABEL org.opencontainers.image.authors="colsrch"

ENV TZ Asia/Shanghai
ENV LANG C.UTF-8
ENV PYTHONPATH=/pkgs
WORKDIR /app
COPY --from=builder /build/__pypackages__/3.9/lib /pkgs
COPY app/ app/
COPY main.py .

RUN pip config set install.prefix /user_pkgs && \
    echo "/user_pkgs/lib/python3.9/site-packages" > /usr/local/lib/python3.9/site-packages/user_pkgs.pth

CMD ["python", "main.py"]
