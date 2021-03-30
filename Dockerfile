FROM agilescience/agilepy-recipe:latest

RUN conda activate agilepydev && \
    git clone https://github.com/AGILESCIENCE/Agilepy.git && \
    cd Agilepy && \
    git checkout ${SOURCE_BRANCH} && \
    python setup.py develop


