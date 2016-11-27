FROM centos:6.8

MAINTAINER Alek  <aleks.cc@gmail.com>

# Install pyenv: https://github.com/yyuu/pyenv-installer
RUN yum install -y \
    zlib-devel \
    bzip2 \
    bzip2-devel \
    readline-devel \
    sqlite \
    sqlite-devel \
    openssl-devel \
    git \
    patch \
    gcc \
    make \
    curl \
    vim; rm -rf /tmp/*; yum clean all

RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | bash

# Load pyenv automatically by adding
# the following to ~/.bash_profile:
RUN \
    echo -e '\n\nexport PATH="/root/.pyenv/bin:$PATH"\neval "$(pyenv init -)"\neval "$(pyenv virtualenv-init -)"\n' >> /root/.bash_profile && \
    source /root/.bash_profile && \
    pyenv install 3.5.2 && \
    pyenv global system 3.5.2

# Add sources
ADD . /root/repo/ca-analytics
WORKDIR /root/repo/ca-analytics

# Install requirements
RUN source /root/.bash_profile && \
    pip3 install -r ./conf/requirements.pip

# Run in container, print output of the script
# TODO: entrypoint
CMD source /root/.bash_profile; ./src/ca_analytics.py
