FROM agilescience/base_image
RUN ls && pwd
RUN conda activate agilepydev && cd / && ls && pwd && python setup.py develop


