FROM agilescience/agilepy-recipe:latest
RUN ls && pwd
RUN cd && ls -alt && pwd

RUN cd && pwd && ls -alt && env
RUN cd /home
RUN echo "$SOURCE_BRANCH"
RUN git clone https://github.com/AGILESCIENCE/Agilepy.git && pwd && ls -alt
RUN git checkout $SOURCE_BRANCH
RUN pwd && ls -alt && env
RUN cd Agilepy
RUN conda activate agilepydev
RUN python setup.py develop


