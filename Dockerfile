FROM agilescience/agilepy-recipe:latest
WORKDIR /tmp
ARG SOURCE_BRANCH

RUN ls && \
    pwd && \
    env && \
    echo "SOURCE_BRANCH: ${SOURCE_BRANCH}"

#RUN conda activate agilepydev && \
#    git clone https://github.com/AGILESCIENCE/Agilepy.git && \
#    cd Agilepy && \
#    echo "SOURCE_BRANCH: ${SOURCE_BRANCH}" && \
#   git checkout ${SOURCE_BRANCH} && \
#    python setup.py develop


