# Set the base image to use for the container
ARG BASE_VERSION=latest
FROM agilescience/agilepy-recipe:${BASE_VERSION}

# Set Working Directory
ARG AGILEPY_RELEASE
WORKDIR /home/flareadvocate

# Install Agilepy dependencies + library
RUN git clone https://github.com/AGILESCIENCE/Agilepy.git 
RUN cd Agilepy && git checkout ${AGILEPY_RELEASE} && git submodule update --init --recursive
RUN cd Agilepy && python3 -m pip install -r requirements.lock
RUN cd Agilepy && python3 -m pip install .

# Add Shared Directory, Entrypoint and Welcome Script
USER root
RUN  mkdir /shared_dir
RUN chown -R flareadvocate:flareadvocate /shared_dir
RUN cp Agilepy/docker/recipes/agilepy/entrypoint.sh /home/flareadvocate/entrypoint.sh
RUN chmod +x /home/flareadvocate/entrypoint.sh
RUN echo "bash /home/flareadvocate/Agilepy/agilepy/scripts/welcome.sh" >> /home/flareadvocate/.bashrc

# Set the user and entrypoint script
USER flareadvocate
ENTRYPOINT ["bash", "/home/flareadvocate/entrypoint.sh"]
