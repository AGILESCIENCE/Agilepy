#!/bin/bash

set -euo pipefail

# -------------------------------
# User and Group Setup
# -------------------------------
USER_NAME=flareadvocate
GROUP_NAME=agile
HOME_DIR="/home/$USER_NAME"


# Current UID/GID in container
CURRENT_UID=$(id -u $USER_NAME)
CURRENT_GID=$(id -g $USER_NAME)

# Target UID/GID from host, defaults if not provided
HOST_UID=${HOST_USER_ID:-1000}
HOST_GID=${HOST_GROUP_ID:-1000}

# Change UID if needed
if [[ "$CURRENT_UID" != "$HOST_UID" ]]; then
    echo "Changing UID of $USER_NAME: $CURRENT_UID -> $HOST_UID"
    usermod -u "$HOST_UID" "$USER_NAME"
    # Update ownership of relevant files
    find /home /shared_dir /tmp -user "$CURRENT_UID" -exec chown -h "$HOST_UID" {} \; 2>/dev/null || true
fi

# Change GID if needed
if [[ "$CURRENT_GID" != "$HOST_GID" ]]; then
    echo "Changing GID of $GROUP_NAME: $CURRENT_GID -> $HOST_GID"
    groupmod -g "$HOST_GID" "$GROUP_NAME"
    # Update group ownership of relevant files
    find /home /shared_dir /tmp -group "$CURRENT_GID" -exec chown -h :"$HOST_GID" {} \; 2>/dev/null || true
fi

# Ensure home directory has correct ownership
chown -R "$USER_NAME":"$USER_NAME" "$HOME_DIR"

# Environment Setup
export HOME="$HOME_DIR"
export USER="$USER_NAME"
export LOGNAME="$USER_NAME"

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

LOG_FILE="entrypoint.log"

echo "PATH: $PATH"                                             | tee -a "$LOG_FILE"
echo "User: $USER_NAME ( $(id -u $USER_NAME) )"                | tee -a "$LOG_FILE"
echo "Python3: $(which python3) $(python3 --version)"          | tee -a "$LOG_FILE"
echo "Jupyter: $(which jupyter) $(jupyter notebook --version)" | tee -a "$LOG_FILE"

# -------------------------------
# Jupyter Server: Optional
# -------------------------------
START_JUPYTER=${START_JUPYTER:-false}

if [[ "$START_JUPYTER" == "true" ]]; then
    # Check for running Jupyter server
    RUNNING=$(jupyter notebook list 2>/dev/null | grep -v "Currently running servers:" || true)

    if [[ -n "$RUNNING" ]]; then
        echo "Existing Jupyter server detected:" | tee -a "$LOG_FILE"
        echo "$RUNNING" | tee -a "$LOG_FILE"
    else
        echo "No Jupyter server. Starting a new one..." | tee -a "$LOG_FILE"
        exec gosu "$USER_NAME" jupyter notebook \
            --ip="*" \
            --port=8888 \
            --no-browser \
            --allow-root \
            --notebook-dir=/shared_dir \
            2>&1 | tee -a "$LOG_FILE"
        echo $! > /tmp/jupyter.pid
        echo "Jupyter server started with PID $(cat /tmp/jupyter.pid)" | tee -a "$LOG_FILE"
    fi
fi

cat $LOG_FILE
echo ""
clear

# Now keep the container alive by running the passed command or just a shell if none provided
if [[ $# -gt 0 ]]; then
    exec gosu $"USER_NAME" "$@"
else
    # Fallback: keep container alive with a tail (or you can use `bash` or another process)
    exec gosu "$USER_NAME" bash
fi
