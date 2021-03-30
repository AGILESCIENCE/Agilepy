FROM agilescience/agilepy-recipe:latest


RUN conda activate agilepydev && \
    git clone https://github.com/AGILESCIENCE/Agilepy.git && \
    cd Agilepy && \
    echo "SOURCE_BRANCH_1: ${SOURCE_BRANCH_1}" && \
    echo "SOURCE_BRANCH_DOLLAR: ${SOURCE_BRANCH_DOLLAR}" && \
    echo "SOURCE_BRANCH_STRING: ${SOURCE_BRANCH_STRING}" && \
    git checkout ${SOURCE_BRANCH} && \
    python setup.py develop


