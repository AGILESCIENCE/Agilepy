FROM oraclelinux:8 AS oracle8

# ---------------------------------- Installing dependencies as root ---------------------------------- 
RUN yum install -y epel-release git cmake3 gcc-c++ gcc binutils \
compat-openssl10 libX11-devel libXpm-devel libXft-devel libXext-devel \ 
gsl-devel openssl-devel wget bzip2-devel libffi-devel xz-devel sqlite-devel \
ncurses ncurses-devel make xz libzstd libzstd-devel which

# ---------------------------------- Install python as root ---------------------------------- 
RUN yum install -y python38 python38-devel
RUN python3 --version
RUN python3 -m pip install --upgrade pip

# ----------------------------------- Install Ruby 2.5.9 as root (Ruby 1.9 does not compile) ----
RUN yum install -y ruby 

# ---------------------------------- Create Agilepy user ---------------------------------- 
RUN groupadd --gid 2007 agilepy
RUN useradd flareadvocate
RUN usermod -a -G agilepy flareadvocate
USER flareadvocate
WORKDIR /home/flareadvocate
RUN mkdir -p /home/flareadvocate/dependencies
SHELL ["/bin/bash", "--login", "-c"]


# ---------------------------------- Installing ROOT as flareadvocate ---------------------------------- 
USER flareadvocate

ENV ROOT_INSTALL=/home/flareadvocate/dependencies/root_install
RUN mkdir -p $ROOT_INSTALL

RUN cd /home/flareadvocate/dependencies && \
    mkdir -p root_src && \
    wget -O ./root_src/root_v6.26.06.tar.gz https://root.cern/download/root_v6.26.06.source.tar.gz && \
    tar -C ./root_src -xzvf ./root_src/root_v6.26.06.tar.gz && \
    rm ./root_src/root_v6.26.06.tar.gz

RUN find /home/flareadvocate/dependencies/root_src -name CMakeLists.txt

RUN cd /home/flareadvocate/dependencies && mkdir -p root_build && cd root_build && \
    cmake  -DPYTHON_EXECUTABLE=/usr/bin/python3 \
           -DCMAKE_INSTALL_PREFIX=${ROOT_INSTALL} \
           ../root_src/root-6.26.06

RUN cd /home/flareadvocate/dependencies/root_build && \
    cmake --build . --target install -j10

RUN echo ". ${ROOT_INSTALL}/bin/thisroot.sh" >> ~/.bashrc


# ---------------------------------- Installing CFITSIO as flareadvocate ---------------------------------- 
RUN cd /home/flareadvocate/dependencies && mkdir -p cfitsio_install && \
    wget http://heasarc.gsfc.nasa.gov/FTP/software/fitsio/c/cfitsio-4.1.0.tar.gz && \
    tar -xzvf cfitsio-4.1.0.tar.gz && \
    rm -rf cfitsio-4.1.0.tar.gz 

RUN cd /home/flareadvocate/dependencies/cfitsio-4.1.0 && \
    ./configure --prefix=/home/flareadvocate/dependencies/cfitsio_install && \
    make && make install

ENV CFITSIO=/home/flareadvocate/dependencies/cfitsio_install
ENV LD_LIBRARY_PATH=$CFITSIO/lib:$LD_LIBRARY_PATH 


# ---------------------------------- Installing science tools as flareadvocate --------------------------------- 
ENV PREFIX=/home/flareadvocate
ENV AGILE=$PREFIX/agiletools 
ENV GSL="" 
ENV C_INCLUDE_PATH=$PREFIX/usr/include CPP_INCLUDE_PATH=$PREFIX/usr/include 
ENV ZLIBPATH=$PREFIX/lib
ENV PFILES=$PFILES:$AGILE/share 
ENV LD_LIBRARY_PATH=$PREFIX/lib:$PREFIX/lib64:/usr/lib64:usr/lib:$LD_LIBRARY_PATH 
ENV PATH=$AGILE/bin:$AGILE/scripts:$PATH

RUN mkdir $PREFIX/agiletools && cd $PREFIX/agiletools && \
    git clone https://github.com/AGILESCIENCE/AGILE-GRID-ScienceTools-Setup.git && cd AGILE-GRID-ScienceTools-Setup \
    && git checkout BUILD26 && ./downloadScienceTools.sh && ./installScienceTools.sh && ./downloadIRF.sh && ./installIRF.sh \
    && rm -rf $AGILE/AGILE-GRID-ScienceTools-Setup

# At the moment, the 'ap' package is not installed but discovered using the PYTHONPATH
#RUN cd $AGILE/scripts && python3 -m pip install .

ENV PATH=$AGILE/scripts/extendesources:$PATH 
ENV LD_LIBRARY_PATH=$AGILE/lib:$LD_LIBRARY_PATH
ENV PYTHONPATH=$AGILE/scripts/ap:$PYTHONPATH 

# ---------------------------------- Install MCAL software --------------------------------- 
# The ssh key is needed to download the MCAL software
# RUN mkdir -p /home/flareadvocate/.ssh
# COPY id_agilepy /home/flareadvocate/.ssh/id_agilepy
# RUN touch /home/flareadvocate/.ssh/known_hosts && ssh-keyscan github.com >> /home/flareadvocate/.ssh/known_hosts
# USER root
# RUN chmod 600 /home/flareadvocate/.ssh/id_agilepy
# RUN chown flareadvocate:flareadvocate /home/flareadvocate/.ssh/id_agilepy
USER flareadvocate

ENV MCALSW=$AGILE/mcalsw
ENV LD_LIBRARY_PATH=$MCALSW/lib:$LD_LIBRARY_PATH

RUN cd /home/flareadvocate/dependencies && \  
    # eval "$(ssh-agent -s)" && ssh-add /home/flareadvocate/.ssh/id_agilepy && \
    # git clone git@github.com:ASTRO-EDU/AGILE-MCAL.git AGILE-MCAL && \
    git clone https://github.com/AGILESCIENCE/AGILE-MCAL.git AGILE-MCAL && \
    cd AGILE-MCAL && git checkout BUILD4 && \
    make && make install  

# Let's delete the ssh key
# RUN rm -r /home/flareadvocate/.ssh
USER flareadvocate

# ----------------------------------  Download the test dataset ---------------------------------- 
RUN mkdir -p $AGILE/agilepy-test-data && \
    cd $AGILE/agilepy-test-data && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1B31SCrHoOU0KnZoaZ7NTq6nY_PTD-ner' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1B31SCrHoOU0KnZoaZ7NTq6nY_PTD-ner" -O test_dataset_6.0.tar.gz && rm -rf /tmp/cookies.txt && \
    tar -xzf test_dataset_6.0.tar.gz && \
    rm test_dataset_6.0.tar.gz && \
    wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1B3Tp-01-X7Cwh6lq11BUCiaHuctj0iDW' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1B3Tp-01-X7Cwh6lq11BUCiaHuctj0iDW" -O test_dataset_agn.tar.gz && rm -rf /tmp/cookies.txt && \
    tar -xzf test_dataset_agn.tar.gz && \
    rm test_dataset_agn.tar.gz



ENV PYTHONPATH=$AGILE/scripts/:$PYTHONPATH
ENV PATH=$AGILE/scripts:$PATH
