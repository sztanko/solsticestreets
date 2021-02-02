# FROM interline/planetutils:release-v0.4.11
FROM sztanko/solsticestreets_base:1.0

ADD .devcontainer /.devcontainer
RUN pip install -r /.devcontainer/requirements.dev.txt
RUN /.devcontainer/install.sh