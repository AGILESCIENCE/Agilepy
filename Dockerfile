FROM agilescience/agilepy-recipe:latest
RUN ls && pwd
RUN cd && ls -alt && pwd

RUN cd && pwd && ls -alt && env
RUN cd /home
RUN echo "$SOURCE_BRANCH"
RUN git clone https://github.com/AGILESCIENCE/Agilepy.git && pwd && ls -alt
RUN cd Agilepy
RUN pwd && ls -alt
RUN git checkout develop
RUN pwd && ls -alt && env
RUN conda activate agilepydev
RUN python setup.py develop


