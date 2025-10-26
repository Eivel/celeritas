FROM python:3.10-slim

RUN set -ex \
    && RUN_DEPS=" \
    libpcre3 \
    postgresql-client \
    " \
    && seq 1 8 | xargs -I{} mkdir -p /usr/share/man/man{} \
    && apt-get update && apt-get install -y --no-install-recommends $RUN_DEPS \
    && rm -rf /var/lib/apt/lists/*

ADD requirements.txt /requirements.txt

RUN set -ex \
    && BUILD_DEPS=" \
    build-essential \
    libpcre3-dev \
    libpq-dev \
    " \
    && apt-get update && apt-get install -y --no-install-recommends $BUILD_DEPS \
    && pip install --no-cache-dir -r /requirements.txt \
    \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false $BUILD_DEPS \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app/
WORKDIR /app/
ADD config /app/config
ADD mods /app/mods
ADD bot.py /app/bot.py

CMD ["python", "bot.py"]
