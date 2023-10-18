##########################################
# Environment variables
##########################################
export condaname="agilepy"
export CFITSIO=$PREFIX
export ROOTSYS=$PREFIX
export AGILE=$PREFIX/agiletools
export GSL=$PREFIX
export C_INCLUDE_PATH=$PREFIX/include
export CPP_INCLUDE_PATH=$PREFIX/include
export ZLIBPATH=$PREFIX/lib

export PFILES=$PFILES:$AGILE/share
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
export LIBRARY_PATH=$PREFIX/lib:$LIBRARY_PATH
export PATH=$AGILE/bin:$AGILE/scripts:$PATH
export BUILD_ANACONDA=true

##########################################
# Agilepy
##########################################
cd $PREFIX/../work
$PYTHON setup.py install


##########################################
# Copying files
##########################################
mkdir -p $AGILE/scripts
mkdir -p $PREFIX/etc/conda/activate.d/
mkdir -p $PREFIX/etc/conda/deactivate.d/
cp $RECIPE_DIR/activate.sh $PREFIX/etc/conda/activate.d/activate_${condaname}.sh
cp $RECIPE_DIR/deactivate.sh $PREFIX/etc/conda/deactivate.d/deactivate_${condaname}.sh
cp $SRC_DIR/agilepy/scripts/* $AGILE/scripts
