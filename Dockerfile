FROM python:3.13-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        gcc \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-wheel && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

FROM base AS builder
COPY ./requirements.txt .
RUN pip install -r requirements.txt

FROM builder AS runtime
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/include /usr/local/include
COPY --from=builder /usr/local/share /usr/local/share
COPY --from=builder /usr/local/bin/python3 /usr/local/bin/python3
COPY ./archiver_ioc.py /app/archiver_ioc.py

CMD ["python", "app/archiver_ioc.py"]