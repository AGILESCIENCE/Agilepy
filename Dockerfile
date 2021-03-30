FROM agilescience/agilepy-recipe:latest


RUN conda activate agilepydev && \
    git clone https://github.com/AGILESCIENCE/Agilepy.git && \
    cd Agilepy && \
    echo "SOURCE_BRANCH: ${SOURCE_BRANCH}" && \
    git checkout ${SOURCE_BRANCH} && \
    python setup.py develop


