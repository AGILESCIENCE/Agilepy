#!/bin/bash
printf "Starting Jupyter Notebook Server...\n"                      > entrypoint.log
printf "Python3 path: $(which python3) $(python3 --version)\n"      > entrypoint.log
printf "Jupyter $(jupyter notebook --version)\n"                    > entrypoint.log
printf "\n\n\n"                                                     > entrypoint.log

# if jupyter server is not running, start it
if [[ $(jupyter notebook list --json) ]]; then
    printf "Jupyter Notebook Server is running at: $(jupyter notebook list --json | jq -r '.base_url')\n" > entrypoint.log
else
    printf "Starting Jupyter Notebook Server...\n" > entrypoint.log
    nohup jupyter notebook --ip="*" --port=8888 --no-browser --allow-root --notebook-dir=/shared_dir > entrypoint.log &
fi

cat entrypoint.log
tail -f /dev/null