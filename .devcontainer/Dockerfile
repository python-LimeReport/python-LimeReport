FROM mcr.microsoft.com/devcontainers/cpp:ubuntu-22.04

ARG AQTINSTALL=3.1.6
ARG QT=6.3.2
ARG QT_MODULES=
ARG QT_HOST=linux
ARG QT_TARGET=desktop
ARG QT_ARCH=
ARG PYTHON=3.9

COPY extra.sh /

RUN . /extra.sh && \
    curl -sfL https://github.com/devcontainers-contrib/nanolayer/releases/download/v0.4.45/nanolayer-x86_64-unknown-linux-gnu.tgz | tar fxvz - -C / && \
    chmod 755 /nanolayer && \
    /nanolayer install \
        apt-get \
        $(packages_to_install) && \
    /nanolayer install \
        devcontainer-feature \
        ghcr.io/devcontainers/features/python:1 \
            --option version="${PYTHON}" && \
    /nanolayer install \
        devcontainer-feature \
        ghcr.io/devcontainers-contrib/features/pipx-package:1 \
            --option package="aqtinstall" \
            --option version="${AQTINSTALL}" && \
    rm /nanolayer

RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 60 --slave /usr/bin/g++ g++ /usr/bin/g++-9

RUN /bin/bash -c 'source /etc/profile && \
aqt install --outputdir /opt/qt ${QT} ${QT_HOST} ${QT_TARGET} ${QT_ARCH} -m ${QT_MODULES}'

ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

USER vscode

ENV PATH /opt/qt/${QT}/gcc_64/bin:$PATH

RUN /bin/bash -c 'source /etc/profile && \
cd $HOME && \
git clone -b ${QT} https://code.qt.io/pyside/pyside-setup.git && \
cd pyside-setup && \
pip install -r requirements.txt && \
python setup.py build --parallel $(nproc) --limited-api yes'

ENV PYSIDE_INSTALL_DIR="/home/vscode/pyside-setup/build/qfpa-py${PYTHON}-qt${QT}-64bit-release/install"