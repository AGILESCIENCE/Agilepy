ARG BASE_VERSION
FROM agilescience/agilepy-recipe:${BASE_VERSION}

WORKDIR /home/flareadvocate

COPY requirements.lock /tmp
RUN cd /home/flareadvocate && python3 -m pip install -r /tmp/requirements.lock

RUN git clone https://github.com/AGILESCIENCE/Agilepy.git 
ARG AGILEPY_RELEASE
RUN cd Agilepy && git checkout ${AGILEPY_RELEASE}
RUN python3 -m pip install -r requirements.lock
RUN python3 -m pip install .

USER root
RUN  mkdir /shared_dir
RUN chown -R flareadvocate:flareadvocate /shared_dir
COPY ./entrypoint.sh /home/flareadvocate/entrypoint.sh
RUN chmod +x /home/flareadvocate/entrypoint.sh
RUN echo "bash /home/flareadvocate/Agilepy/agilepy/scripts/welcome.sh" >> /home/flareadvocate/.bashrc

USER flareadvocate
ENTRYPOINT ["bash", "/home/flareadvocate/entrypoint.sh"]