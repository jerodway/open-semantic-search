FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install --no-install-recommends --yes \
    python3-requests \
    python3-dateutil \
    python3-lxml \
    python3-feedparser \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-dev \
    nfs-common \
    cifs-utils \
    iputils-ping \
    nano \
    libreoffice \
    libreoffice-java-common \
    default-jre \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

    #libreoffice \
    #libreoffice-java-common \
    #default-jre \

RUN pip3 install --no-cache-dir Flask

RUN mkdir -p /usr/src/app
COPY ./src /usr/src/app

RUN mkdir -p /shared/temp
COPY ./test.pdf /shared/temp

CMD exec /usr/bin/python3 /usr/src/app/app.py
