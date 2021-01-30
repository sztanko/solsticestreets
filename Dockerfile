# FROM interline/planetutils:release-v0.4.11
FROM andrejreznik/python-gdal:py3.7.3-gdal3.0.0
ENV PATH /usr/local/bin:$PATH

ADD .devcontainer /.devcontainer
RUN echo "deb http://ftp.debian.org/debian stretch-backports main"  > /etc/apt/sources.list.d/backports.list
RUN apt-get update && apt-get install -y unzip build-essential wget virtualenv libspatialindex-dev python-rtree git osmium-tool htop jq && apt -t stretch-backports install osmium-tool
RUN wget -c https://github.com/cli/cli/releases/download/v1.5.0/gh_1.5.0_linux_amd64.deb  && dpkg -i gh_1.5.0_linux_amd64.deb && rm gh_1.5.0_linux_amd64.deb
RUN pip install --upgrade pip
RUN pip install -r /.devcontainer/requirements.dev.txt
RUN /.devcontainer/install.sh