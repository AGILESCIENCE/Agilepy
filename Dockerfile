FROM agilescience/agilepy-recipe:latest
RUN ls && pwd
RUN conda activate agilepydev && cd / && pwd && ls -alt && python setup.py develop


