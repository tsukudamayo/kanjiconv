FROM python:3.6.9-buster

RUN mkdir -p /kytea/app
WORKDIR /kytea/app
COPY . .
ENV LANG ja_JP.UTF-8
ENV LC_TYPE jp_JP.UTF-8
RUN apt-get update \
    && apt-get -y install emacs \
    llvm \
    clang \
    libclang-dev \
    locales \
    && git clone https://github.com/tsukudamayo/dotfiles.git \
    && cp -r ./dotfiles/linux/.emacs.d ~/ \
    && cp -r ./dotfiles/.fonts ~/ \
    && wget https://github.com/Kitware/CMake/releases/download/v3.16.1/cmake-3.16.1.tar.gz \ 
    && tar xvf cmake-3.16.1.tar.gz \
    && rm cmake-3.16.1.tar.gz \
    && locale-gen jp_JP.UTF8 \
    && localedef -f UTF-8 -i ja_JP ja_JP.utf8

RUN pip install -r requirements.txt \
    && wget http://www.phontron.com/kytea/download/kytea-0.4.7.tar.gz \
    && tar xzf kytea-0.4.7.tar.gz

WORKDIR /kytea/app/cmake-3.16.1
RUN ./bootstrap && make && make install

WORKDIR /kytea/app
RUN rm -rf cmake-3.16.1

WORKDIR kytea-0.4.7

RUN ./configure \
    && make \
    && make install \
    && ldconfig

RUN wget http://www.ar.media.kyoto-u.ac.jp/mori/research/topics/NER/2014-05-28-RecipeNE-sample.tar.gz \
    && tar xvf 2014-05-28-RecipeNE-sample.tar.gz

RUN mkdir -p model

WORKDIR model
RUN wget http://www.phontron.com/kytea/download/model/jp-0.4.7-1.mod.gz \
    && gzip -d jp-0.4.7-1.mod.gz

WORKDIR /kytea/app

EXPOSE 5000

CMD ["/bin/bash"]
