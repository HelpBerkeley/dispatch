FROM ubuntu:xenial

WORKDIR /home/

# set environment variables
ENV GOVERSION 1.14.1
ENV GOROOT /opt/go
ENV GOPATH /go
ENV PATH $PATH:$GOROOT/go/bin:$GOPATH/bin:/opt/miniconda/bin

RUN apt-get update --yes && \
        apt-get --yes install git wget curl

# download golang
RUN mkdir -p ${GOROOT} && \
    cd /opt && \
    curl -s -L https://golang.org/dl/go${GOVERSION}.linux-amd64.tar.gz | tar zxv && \
    ln -f -s /opt/go/bin/go /usr/bin/ && \
    mkdir -p ${GOPATH}/bin

RUN go get github.com/gorilla/mux

# dowload and install miniconda
RUN cd /opt && \
    curl -O -s -L https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh && \
    bash Miniconda3-latest-Linux-x86_64.sh -b -p ./miniconda

RUN conda install jupyter -y
