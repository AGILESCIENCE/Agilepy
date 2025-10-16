# Set the base image to use for the container
ARG BASE_VERSION=latest
FROM agilescience/agilepy-recipe:${BASE_VERSION}
ARG AGILEPY_RELEASE=main

# Set Working Directory
WORKDIR /home/flareadvocate

# Clone Agilepy, install dependencies and library
RUN git clone --recursive https://github.com/AGILESCIENCE/Agilepy.git && \
    cd Agilepy && \
    git checkout ${AGILEPY_RELEASE} && \
    git submodule update --init --recursive && \
    python3 -m pip install --no-cache-dir --upgrade "pip==25.0.1" && \
    python3 -m pip install --no-cache-dir -r requirements.lock && \
    python3 -m pip install --no-cache-dir .

# Download the test dataset, print message if it fails
RUN if ! download_test_dataset.sh; then \
      echo "!!! WARNING: Test dataset download failed during build." >&2; \
      echo "    You can manually rerun it inside the container with: download_test_dataset.sh"; \
    fi

# Add Gosu for user management, Shared Directory, Entrypoint and Welcome Script
USER root
RUN wget -O /usr/local/bin/gosu https://github.com/tianon/gosu/releases/download/1.19/gosu-amd64 && \
    chmod +x /usr/local/bin/gosu && \
    gosu nobody true && \
    yum clean all && rm -rf /var/cache/yum
RUN mkdir /shared_dir && \
    chown -R flareadvocate:flareadvocate /shared_dir && \
    cp Agilepy/docker/recipes/agilepy/entrypoint.sh /home/flareadvocate/entrypoint.sh && \
    chmod +x /home/flareadvocate/entrypoint.sh && \
    echo "bash /home/flareadvocate/Agilepy/agilepy/scripts/welcome.sh" >> /home/flareadvocate/.bashrc

# Set entrypoint
ENTRYPOINT ["bash", "/home/flareadvocate/entrypoint.sh"]
