FROM agilescience/agilepy-recipe:latest
RUN ls && pwd
RUN cd && ls -alt && pwd

RUN conda activate agilepydev 
RUN cd && pwd && ls -alt 
RUN python setup.py develop


