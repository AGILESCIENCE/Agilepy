#!/bin/bash

set -e

# Add local bin to PATH
export PATH="/home/flareadvocate/.local/bin:$PATH"

# Set the log file
LOG_FILE="entrypoint.log"
echo "PATH: $PATH"
echo "Starting Jupyter Notebook Server..."                 | tee -a "$LOG_FILE"
echo "Python3 path: $(which python3) $(python3 --version)" | tee -a "$LOG_FILE"
echo "Python3 path: $(which jupyter)"                      | tee -a "$LOG_FILE"
echo "Jupyter $(jupyter notebook --version)"               | tee -a "$LOG_FILE"
echo ""                                                    | tee -a "$LOG_FILE"

# Check for running Jupyter server
RUNNING=$(jupyter notebook list 2>/dev/null | grep -v "Currently running servers:" || true)

if [[ -n "$RUNNING" ]]; then
    echo "An existing Jupyter server is already running:" | tee -a "$LOG_FILE"
    echo "$RUNNING" | tee -a "$LOG_FILE"
else
    echo "No existing Jupyter server found. Starting a new one..." | tee -a "$LOG_FILE"
    jupyter notebook --ip="*" --port=8888 --no-browser --allow-root --notebook-dir=/shared_dir 2>&1 | tee -a "$LOG_FILE" &
    echo $! > /tmp/jupyter.pid
    echo "Jupyter server started with PID $(cat /tmp/jupyter.pid)" | tee -a "$LOG_FILE"
fi

cat $LOG_FILE
echo ""
clear

# Now keep the container alive by running the passed command or just a shell if none provided
if [[ $# -gt 0 ]]; then
    exec "$@"
else
    # fallback: keep container alive with a tail (or you can use `bash` or another process)
    tail -f /dev/null
fi
