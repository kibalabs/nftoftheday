FROM python:3.10.9-slim

RUN apt-get update && apt-get install --yes --no-install-recommends make

WORKDIR /app

# NOTE(krishan711): GCC (and others) needed to build some dependencies. Remove when everything has a wheel.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libc-dev \
    && pip install lru-dict==1.1.8 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc libc-dev

COPY makefile $WORKDIR
COPY requirements-dev.txt $WORKDIR
COPY requirements.txt $WORKDIR
RUN make install

COPY . $WORKDIR

EXPOSE 5000
CMD ["make", "start-prod"]
