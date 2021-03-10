FROM agilescience/agilepy-recipe:latest
RUN ls && pwd
RUN cd && ls -alt && pwd

RUN cd && pwd && ls -alt 
RUN cd /home
RUN git clone --branch "$SOURCE_BRANCH" https://github.com/AGILESCIENCE/Agilepy.git && pwd && ls -alt
RUN pwd && ls -alt
RUN cd Agilepy
RUN conda activate agilepydev
RUN python setup.py develop


