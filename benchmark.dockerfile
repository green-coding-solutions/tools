FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        coreutils \
        curl \
        procps \
        stress-ng \
        wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY benchmark.sh /app/benchmark.sh
RUN chmod +x /app/benchmark.sh

CMD ["sleep", "infinity"]
