ARG VER="3.10.13"
FROM python:${VER}-slim

EXPOSE 8088

ENV TZ=Asia/Tokyo

# 日本語環境の設定
# ENV LANG ja_JP.UTF-8
# ENV LC_ALL ja_JP.UTF-8
# RUN sed -i '$d' /etc/locale.gen \
#     && echo "ja_JP.UTF-8 UTF-8" >> /etc/locale.gen \
#     && locale-gen ja_JP.UTF-8 \
#     && /usr/sbin/update-locale LANG=ja_JP.UTF-8 LANGUAGE="ja_JP:ja"
# RUN /bin/bash -c "source /etc/default/locale"
# RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime

# 日本語フォントのインストール
RUN apt-get update && apt-get install -y \
    fonts-ipaexfont \
    libopencv-dev \
    lhasa \
    fonts-noto-cjk && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
