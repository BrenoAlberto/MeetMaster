#!/bin/bash

set -e

if [ "$RUNNING_IN_DOCKER" = "true" ]; then
  exit 0
fi

USER_ID=$(id -u)
GROUP_ID=$(id -g)
USER_NAME="meet-dev"

USER_HOME="/home/$USER_NAME"
MAIN_DIR="$USER_HOME/MeetMaster"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MAIN_LOCAL_DIR="$(cd "$SCRIPT_DIR/../../" && pwd)"

ENV_FILE="$SCRIPT_DIR/../.env"

> $ENV_FILE

env_vars=(
  "USER_ID" "GROUP_ID" "USER_NAME" "USER_HOME"
  "MAIN_LOCAL_DIR" "MAIN_DIR"
)

for var in "${env_vars[@]}"; do
  echo "$var=${!var}" >> $ENV_FILE
done
