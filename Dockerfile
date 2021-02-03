FROM sztanko/solsticestreets_base:latest

ADD .devcontainer /.devcontainer
RUN pip install -r /.devcontainer/requirements.dev.txt
RUN /.devcontainer/install.sh