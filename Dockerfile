FROM ubuntu:22.04

WORKDIR /usr/src/app
SHELL ["/bin/bash", "-c"]
RUN chmod 777 /usr/src/app

RUN apt-get -y update && DEBIAN_FRONTEND="noninteractive" \
    apt-get install -y python3 python3-pip aria2 qbittorrent-nox \
    tzdata p7zip-full p7zip-rar xz-utils curl pv jq ffmpeg wget \
    locales git unzip rtmpdump libmagic-dev libcurl4-openssl-dev \
    libssl-dev libc-ares-dev libsodium-dev libcrypto++-dev \
    libsqlite3-dev libfreeimage-dev libpq-dev libffi-dev \
    && locale-gen en_US.UTF-8 && \
    curl -L https://github.com/anasty17/megasdkrest/releases/download/latest/megasdkrest-$(cpu=$(uname -m);\
    if [[ "$cpu" == "x86_64" ]]; then echo "amd64"; elif [[ "$cpu" == "x86" ]]; \
    then echo "i386"; elif [[ "$cpu" == "aarch64" ]]; then echo "arm64"; else echo $cpu; fi) \
    -o /usr/local/bin/megasdkrest && chmod +x /usr/local/bin/megasdkrest

# Installing Mediainfo Latest
RUN wget -O ./libzen0v5_0.4.39-1_amd64.xUbuntu_20.04.deb https://mediaarea.net/download/binary/libzen0/0.4.39/libzen0v5_0.4.39-1_amd64.xUbuntu_20.04.deb \
    && apt install -y ./libzen0v5_0.4.39-1_amd64.xUbuntu_20.04.deb && rm ./libzen0v5_0.4.39-1_amd64.xUbuntu_20.04.deb \
    && wget -O ./libmediainfo0v5_21.09-1_amd64.xUbuntu_20.04.deb https://mediaarea.net/download/binary/libmediainfo0/21.09/libmediainfo0v5_21.09-1_amd64.xUbuntu_20.04.deb \
    && apt install -y ./libmediainfo0v5_21.09-1_amd64.xUbuntu_20.04.deb && rm ./libmediainfo0v5_21.09-1_amd64.xUbuntu_20.04.deb \
    && wget -O ./mediainfo_21.09-1_amd64.xUbuntu_20.04.deb https://mediaarea.net/download/binary/mediainfo/21.09/mediainfo_21.09-1_amd64.xUbuntu_20.04.deb \
    && apt install -y ./mediainfo_21.09-1_amd64.xUbuntu_20.04.deb && rm ./mediainfo_21.09-1_amd64.xUbuntu_20.04.deb

ENV LANG="en_US.UTF-8" LANGUAGE="en_US:en"

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD ["bash", "start.sh"]