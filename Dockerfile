FROM python:latest

# set the working directory
WORKDIR /workspaces/peloton

# install some useful stuff
RUN apt-get -y update && apt-get -y install nano

# # Create the user
ARG USERNAME=peloton
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    # [Optional] Add sudo support. Omit if you don't need to install software after connecting.
    && apt-get update \
    && apt-get install -y sudo \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /tmp/requirements.txt && rm /tmp/requirements.txt

# copy the scripts to the folder
# COPY . /streamlit

# [Optional] Set the default user. Omit if you want to keep the default as root.
USER $USERNAME

# start the server
CMD ["fastapi", "run", "main.py", "--reload"]