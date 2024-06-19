FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install wget git sudo -y

# Set up user
ARG USER_ID
ARG GROUP_ID
ARG USER_NAME
RUN groupadd -o -r --gid ${GROUP_ID} ${USER_NAME} \
  && adduser --uid $USER_ID --ingroup ${USER_NAME} --disabled-password --gecos "" ${USER_NAME} \
  && echo "${USER_NAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers \
  && sudo -lU ${USER_NAME} \
  && sudo usermod -aG sudo ${USER_NAME}

ENV RUNNING_IN_DOCKER true

RUN apt-get install -y python3-pip python3.10-dev python3.10-venv \
  && update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1 \
  && update-alternatives --install /usr/bin/python python /usr/bin/python3.10 1

# Install Oh My Zsh
USER ${USER_NAME}
RUN sh -c "$(wget -O- https://github.com/deluan/zsh-in-docker/releases/download/v1.2.0/zsh-in-docker.sh)" -- \
  -t https://github.com/denysdovhan/spaceship-prompt \
  -p git \
  -p ssh-agent \
  -p https://github.com/zsh-users/zsh-autosuggestions \
  -p https://github.com/zsh-users/zsh-completions \
  -p https://github.com/zsh-users/zsh-syntax-highlighting \
  -p https://github.com/zsh-users/zsh-history-substring-search

USER root
RUN apt-get --fix-broken install -y \
  && apt-get autoremove -y \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

USER ${USER_NAME}

ARG MAIN_DIR
WORKDIR ${MAIN_DIR}

# prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# ensure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED 1

ENV RUNNING_IN_DEV_CONTAINER true

RUN echo "alias venv='source ${MAIN_DIR}/.devcontainer/scripts/start.sh'" >> ~/.zshrc

ENV PRE_COMMIT_HOME=${MAIN_DIR}/.devcontainer/pre-commit

CMD ["/bin/zsh"]
