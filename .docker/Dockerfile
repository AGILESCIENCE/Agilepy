FROM agilescience/agilepy-recipe:latest

ARG SOURCE_BRANCH_REPO

RUN conda activate agilepydev && \
    git clone https://github.com/AGILESCIENCE/Agilepy.git --branch ${SOURCE_BRANCH_REPO} && \
    cd Agilepy && \
    python setup.py develop


